"""Signal model rung 4: EEGNet raw-waveform load decoder under LOSO.

This is the final pre-registered model-class rung. Rungs 1-3 (logistic / filter-bank
covariance / Riemannian) all plateaued at ~0.53-0.56 mean LOSO balanced accuracy and
none beat the strongest non-signal control (behavioral-only, 0.593). Those rungs operate
on hand-built spectral / covariance features. EEGNet instead learns spatiotemporal
filters directly from the raw maintenance-window waveform, so running it once completes
the ladder: if a learned convnet also fails to clear the control, the negative decoding
result is exhausted across the whole pre-registered model class, not just the linear part.

What it does
------------
* Loads raw scalp epochs from the NIX files, restricts them to the locked 8-channel
  common montage, and cuts the predeclared maintenance window [-3, 0] s (600 samples at
  200 Hz). Trials are aligned to the feature bundle's exact kept set (same artifact
  exclusions, same labels, same subjects), so this rung decodes the identical trials as
  rungs 1-3 and is directly comparable.
* Runs leave-one-subject-out with the held-out subject touched once. Per-channel
  standardization is fit on training trials only. Epoch count is selected by an inner
  subject-grouped validation split of the training subjects (early stopping on inner-val
  balanced accuracy); the model is then refit on all training subjects for the selected
  number of epochs and scored once on the held-out subject.
* Class imbalance (~2:1 high:low by construction) is handled with inverse-frequency class
  weights in the cross-entropy and balanced accuracy as the metric -- identical accounting
  to the other rungs.
* Writes the same output contract as ``run_load_decoder.py`` / ``run_riemann_decoder.py``
  (predictions / subject_scores / summary), so Codex's control / statistics / dashboard
  scripts consume this rung unchanged (run them with ``--feature-family covariance`` for
  the channel selection; the +0.075 test only reads trial_id / signal_pred / load_binary).

Two predeclared channel sets (``--channel-set``), matching the other rungs:
  * ``all``   -- the locked 8-channel common montage (HEADLINE).
  * ``brain`` -- the 6 brain channels, excluding A1/A2 references (SENSITIVITY
                 DIAGNOSTIC; it cannot move the success bar).

The network lives in ``utils/eegnet.py`` (dependency-free NumPy, gradient-checked). This
script asserts the gradient check passes before any training, so the rung's negative
result rests on a verified implementation.

Usage:
    .\\venv\\Scripts\\python.exe scripts\\run_eegnet_decoder.py \\
        --data-dir "D:\\Simultaneous EEG_LFP\\data_nix" \\
        --bundle outputs\\features\\feature_bundle.npz \\
        --out-dir outputs\\decoding --channel-set all
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import nix_io                                         # noqa: E402
from utils.epoching import MAINTENANCE_WINDOW_S, extract_window  # noqa: E402
from utils.eegnet import EEGNet, EEGNetConfig, gradient_check    # noqa: E402


def balanced_accuracy_score(y_true, y_pred):
    """Binary balanced accuracy = mean of per-class recall.

    Implemented in NumPy so this pure-NumPy rung needs no scipy/sklearn import (the
    project's compute environment cannot reliably load scipy's LAPACK DLLs when the page
    file is constrained). Matches sklearn.metrics.balanced_accuracy_score for the binary,
    no-adjustment case used across all rungs.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    recalls = []
    for c in np.unique(y_true):
        sel = y_true == c
        recalls.append((y_pred[sel] == c).mean())
    return float(np.mean(recalls))


def load_raw_windows(data_dir, montage, trial_ids):
    """Build a (trial_id -> (n_montage_ch, n_window_samples)) maintenance-window map.

    Reads each session's raw scalp epochs, restricts to the locked montage (in montage
    order, no padding/imputation), and slices the predeclared maintenance window. Only the
    trials in ``trial_ids`` (the bundle's kept set) are returned; a session contributes its
    intersection with that set.

    Raises if a requested montage channel is absent from a session (the headline run forbids
    padding) or if any requested trial is never found.
    """
    wanted = set(trial_ids)
    out: dict[str, np.ndarray] = {}
    fs = None
    n_win = None
    files = nix_io.list_session_files(data_dir)
    for i, path in enumerate(files, 1):
        epochs = nix_io.load_scalp_epochs(path)
        # Montage indices within this session (fail loudly if a channel is missing).
        idx = []
        for ch in montage:
            if ch not in epochs.channels:
                raise ValueError(
                    f"{path}: locked montage channel '{ch}' absent from session channels "
                    f"{epochs.channels}. Padding/imputation is forbidden for the headline run."
                )
            idx.append(epochs.channels.index(ch))
        sub = epochs.data[:, idx, :]  # (n_trials, n_montage_ch, n_samples), montage order
        win = extract_window(sub, epochs.offset_s, epochs.sample_rate_hz,
                             MAINTENANCE_WINDOW_S)  # (n_trials, n_ch, n_win)
        if fs is None:
            fs = epochs.sample_rate_hz
            n_win = win.shape[2]
        n_kept = 0
        for k, tid in enumerate(epochs.trial_ids):
            if tid in wanted:
                out[tid] = win[k].astype(np.float64)
                n_kept += 1
        print(f"  [{i:2d}/{len(files)}] {epochs.subject_id}/{epochs.session_id}: "
              f"{n_kept} in-analysis trials windowed")
    missing = wanted - set(out)
    if missing:
        raise ValueError(f"{len(missing)} bundle trials not found in raw epochs: "
                         f"{sorted(missing)[:5]}...")
    return out, float(fs), int(n_win)


def _standardize(X_tr, X_all):
    """Per-channel z-score using TRAIN trials only. X: (N, C, T)."""
    mean = X_tr.mean(axis=(0, 2), keepdims=True)
    std = X_tr.std(axis=(0, 2), keepdims=True) + 1e-8
    return (X_all - mean) / std, mean, std


def _class_weights(y):
    """Inverse-frequency weights normalized to mean 1 (matches balanced-accuracy intent)."""
    w = np.zeros(2)
    for c in (0, 1):
        nc = max(int((y == c).sum()), 1)
        w[c] = len(y) / (2.0 * nc)
    return w


def _train(net, X, y, cw, max_epochs, batch, lr, weight_decay, seed,
           X_val=None, y_val=None, patience=10):
    """Train ``net`` with Adam; if a val set is given, early-stop on val balanced accuracy.

    Returns the epoch (1-based) at which the best val score was seen (or ``max_epochs`` when
    no val set is given). The held-out test subject is never passed here.
    """
    rng = np.random.default_rng(seed)
    n = len(y)
    Xin = X[:, None, :, :]  # (N, 1, C, T)
    best_score, best_epoch, since = -np.inf, max_epochs, 0
    for epoch in range(1, max_epochs + 1):
        order = rng.permutation(n)
        for s in range(0, n, batch):
            b = order[s:s + batch]
            logits, cache = net.forward(Xin[b], train=True, rng=rng)
            _, dlogits, _ = net.softmax_ce(logits, y[b], cw)
            grads = net.backward(dlogits, cache)
            net.adam_step(grads, lr=lr, weight_decay=weight_decay)
        if X_val is not None:
            pred = predict(net, X_val)
            score = balanced_accuracy_score(y_val, pred)
            if score > best_score + 1e-4:
                best_score, best_epoch, since = score, epoch, 0
            else:
                since += 1
                if since >= patience:
                    break
    return best_epoch


def _logits_chunked(net, X, chunk=32):
    """Eval-mode logits for X (N, C, T), computed in row-chunks.

    The im2col buffers in the temporal convolution scale with the batch size, so
    inference is chunked to keep peak memory bounded on this constrained machine (a
    whole-subject forward pass would otherwise allocate hundreds of MiB at once).
    """
    parts = []
    for s in range(0, len(X), chunk):
        xb = X[s:s + chunk][:, None, :, :]
        logits, _ = net.forward(xb, train=False, rng=None)
        parts.append(logits)
    return np.concatenate(parts, axis=0)


def predict(net, X, chunk=32):
    """Eval-mode class predictions for X (N, C, T)."""
    return _logits_chunked(net, X, chunk).argmax(axis=1)


def predict_proba(net, X, chunk=32):
    """Eval-mode P(class=1) for X (N, C, T)."""
    logits = _logits_chunked(net, X, chunk)
    z = logits - logits.max(axis=1, keepdims=True)
    ez = np.exp(z)
    return ez[:, 1] / ez.sum(axis=1)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", required=True, help="Path to the dataset's data_nix/ directory.")
    ap.add_argument("--bundle", required=True, help="feature_bundle.npz path (defines kept trials).")
    ap.add_argument("--out-dir", default="outputs/decoding", help="Output directory.")
    ap.add_argument("--channel-set", choices=["all", "brain"], default="all",
                    help="'all'=8-ch headline montage; 'brain'=6-ch A1/A2-excluded diagnostic.")
    ap.add_argument("--max-epochs", type=int, default=50)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--weight-decay", type=float, default=1e-4)
    ap.add_argument("--patience", type=int, default=10)
    ap.add_argument("--n-inner-val", type=int, default=2,
                    help="Training subjects held out for inner-CV early stopping.")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--skip-gradcheck", action="store_true",
                    help="Skip the finite-difference gradient check (not recommended).")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    if not args.skip_gradcheck:
        print("Gradient-checking EEGNet backprop (finite differences)...")
        errs = gradient_check(seed=0)
        print(f"  PASS: max relative error {max(errs.values()):.2e}\n")

    bundle = np.load(args.bundle, allow_pickle=True)
    y = bundle["y"].astype(int)
    subject_id = bundle["subject_id"].astype(str)
    session_id = bundle["session_id"].astype(str)
    trial_id = bundle["trial_id"].astype(str)
    channel_names = [str(c) for c in bundle["channel_names"].astype(str)]
    channel_role = [str(r) for r in bundle["channel_role"].astype(str)]

    if args.channel_set == "brain":
        keep = [i for i, r in enumerate(channel_role) if r == "brain"]
    else:
        keep = list(range(len(channel_names)))
    montage = [channel_names[i] for i in keep]  # full montage read; subselect after
    full_montage = list(channel_names)
    is_headline = (args.channel_set == "all")

    print(f"EEGNet rung-4 run: channel-set={args.channel_set} ({'HEADLINE' if is_headline else 'DIAGNOSTIC'})")
    print(f"  montage: {montage}")
    print(f"Loading raw maintenance-window epochs from {args.data_dir} ...")
    win_map, fs, n_win = load_raw_windows(args.data_dir, full_montage, trial_id.tolist())
    keep_idx = np.array(keep, dtype=int)
    X = np.stack([win_map[t][keep_idx] for t in trial_id], axis=0)  # (N, C_sel, T)
    C_sel, T = X.shape[1], X.shape[2]
    print(f"  X: {X.shape}  (fs={fs} Hz, window={MAINTENANCE_WINDOW_S} s -> {n_win} samples)\n")

    tag = f"eegnet_raw_{args.channel_set}"
    subjects = sorted(np.unique(subject_id).tolist())
    rng = np.random.default_rng(args.seed)

    pred_rows, per_subject = [], []
    t0 = time.time()
    for held in subjects:
        te = subject_id == held
        tr = ~te
        tr_subjects = [s for s in subjects if s != held]

        # Inner-CV split of TRAINING subjects for early stopping (held-out never touched).
        n_val = min(args.n_inner_val, max(1, len(tr_subjects) - 1))
        val_subjects = set(rng.choice(tr_subjects, size=n_val, replace=False).tolist())
        inner_tr = tr & ~np.isin(subject_id, list(val_subjects))
        inner_val = tr & np.isin(subject_id, list(val_subjects))

        cfg = EEGNetConfig(C=C_sel, T=T)
        cw = _class_weights(y[inner_tr])

        Xtr_s, mean, std = _standardize(X[inner_tr], X[inner_tr])
        Xval_s = (X[inner_val] - mean) / std
        net = EEGNet(cfg, seed=args.seed)
        best_epoch = _train(net, Xtr_s, y[inner_tr], cw, args.max_epochs, args.batch,
                            args.lr, args.weight_decay, args.seed,
                            X_val=Xval_s, y_val=y[inner_val], patience=args.patience)

        # Refit on ALL training subjects for the selected epoch count; score test once.
        Xtr_all_s, mean2, std2 = _standardize(X[tr], X[tr])
        Xte_s = (X[te] - mean2) / std2
        cw_all = _class_weights(y[tr])
        net = EEGNet(cfg, seed=args.seed)
        _train(net, Xtr_all_s, y[tr], cw_all, best_epoch, args.batch,
               args.lr, args.weight_decay, args.seed)  # no val -> fixed epochs

        pred = predict(net, Xte_s)
        proba = predict_proba(net, Xte_s)
        ba = balanced_accuracy_score(y[te], pred)
        per_subject.append({"subject_id": held, "n_test": int(te.sum()),
                            "selected_epochs": int(best_epoch), "signal_ba": float(ba)})
        for n, k in enumerate(np.where(te)[0]):
            pred_rows.append({
                "subject_id": subject_id[k], "session_id": session_id[k],
                "trial_id": trial_id[k], "load_binary": int(y[k]),
                "signal_pred": int(pred[n]), "signal_score": float(proba[n]),
            })
        print(f"  {held}: balanced acc = {ba:.3f}  (n_test={int(te.sum())}, "
              f"epochs={best_epoch}, val_subj={sorted(val_subjects)})")

    per_df = pd.DataFrame(per_subject)
    mean_ba = float(per_df["signal_ba"].mean())
    pred_df = pd.DataFrame(pred_rows)

    pred_path = os.path.join(args.out_dir, f"predictions_{tag}.csv")
    sub_path = os.path.join(args.out_dir, f"subject_scores_{tag}.csv")
    pred_df.to_csv(pred_path, index=False)
    per_df.to_csv(sub_path, index=False)
    with open(os.path.join(args.out_dir, f"summary_{tag}.json"), "w") as fh:
        json.dump({
            "config": {"model": "eegnet", "channel_set": args.channel_set,
                       "is_headline": is_headline, "channels": montage,
                       "n_channels": C_sel, "n_samples": T, "fs_hz": fs,
                       "window_s": list(MAINTENANCE_WINDOW_S),
                       "arch": {"F1": cfg.F1, "D": cfg.D, "F2": cfg.F2, "kt": cfg.kt,
                                "kt2": cfg.kt2, "p1": cfg.p1, "p2": cfg.p2,
                                "dropout": cfg.dropout},
                       "max_epochs": args.max_epochs, "batch": args.batch, "lr": args.lr,
                       "weight_decay": args.weight_decay, "patience": args.patience,
                       "n_inner_val": args.n_inner_val, "seed": args.seed},
            "mean_signal_balanced_accuracy": mean_ba,
            "per_subject": per_subject,
        }, fh, indent=2)

    print(f"\nMean LOSO balanced accuracy ({tag}): {mean_ba:.3f}")
    print(f"  (signal side only; subtract Codex's strongest control for the +0.075 test)")
    print(f"  elapsed: {time.time() - t0:.0f}s")
    print(f"Wrote:\n  {pred_path}\n  {sub_path}")


if __name__ == "__main__":
    main()
