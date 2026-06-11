"""Signal model rung 1: regularized logistic / LDA load decoder under LOSO.

This is the scalp-only signal model the headline claim rests on. It decodes WM load
(high 6/8 vs low 4) from maintenance-window scalp features, evaluated leave-one-subject-
out so the number reported for each subject is a genuine cross-subject prediction.

Discipline enforced here (Claim Sheet + Codex's controls spec):
  * Held-out subject is touched once. All preprocessing (standardization) and any
    hyperparameter selection (the logistic regularization strength C) are fit using the
    training subjects only, via an inner subject-grouped CV; the held-out subject is
    scored a single time with the frozen pipeline.
  * Balanced accuracy is the metric (the high class pools set sizes 6 and 8, so the
    classes are ~2:1 imbalanced by construction).
  * The output is the signal side of the evidence only. Codex's control models consume
    the same folds and the same metadata to compute behavioral / timing / shuffle
    baselines, and the per-subject improvement = signal_ba - strongest_control_ba is
    computed in his statistics step, not here.

Two predeclared configurations (select with --channel-set):
  * ``all``   -- the locked 8-channel common montage (HEADLINE result).
  * ``brain`` -- the 6 common brain channels, excluding A1/A2 ear/mastoid references
                 (the predeclared reference/artifact SENSITIVITY DIAGNOSTIC; it cannot
                 move the success bar, but a headline dominated by A1/A2 is a red flag).

Usage:
    .\\venv\\Scripts\\python.exe scripts\\run_load_decoder.py \\
        --bundle outputs\\features\\feature_bundle.npz --out-dir outputs\\decoding \\
        --model logistic --feature-family band_power --channel-set all
"""

from __future__ import annotations

import argparse
import json
import os

import numpy as np
import pandas as pd
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler

# Inner-CV grid for the logistic regularization strength (selected on training subjects).
C_GRID = [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0]


def _select_columns(bundle, feature_family: str, channel_set: str):
    """Return the column indices for the requested feature family and channel set.

    Args:
        bundle: loaded npz.
        feature_family: 'band_power', 'covariance', or 'all'.
        channel_set: 'all' (8-ch montage) or 'brain' (exclude A1/A2 references).

    Returns:
        (col_indices, kept_channel_names) -- columns whose family and channels match.
    """
    families = bundle["feature_family"].astype(str)
    names = bundle["feature_names"].astype(str)
    channel_names = bundle["channel_names"].astype(str)
    channel_role = bundle["channel_role"].astype(str)

    if channel_set == "brain":
        kept_channels = [c for c, r in zip(channel_names, channel_role) if r == "brain"]
    else:
        kept_channels = list(channel_names)
    kept_set = set(kept_channels)

    cols = []
    for j, (nm, fam) in enumerate(zip(names, families)):
        if feature_family != "all" and fam != feature_family:
            continue
        # Feature name encodes channels as 'bp__<ch>__band' or 'cov__<ch>[-<ch>]__band'.
        token = nm.split("__")[1]
        chans = token.split("-")
        if all(ch in kept_set for ch in chans):
            cols.append(j)
    if not cols:
        raise ValueError(f"No columns match family={feature_family}, channel_set={channel_set}.")
    return np.array(cols, dtype=int), kept_channels


def _make_model(model_name: str, C: float):
    """Construct the classifier for one fit (logistic with given C, or shrinkage LDA)."""
    if model_name == "logistic":
        return LogisticRegression(penalty="l2", C=C, solver="liblinear", max_iter=2000)
    if model_name == "lda":
        return LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")
    raise ValueError(f"Unknown model '{model_name}' (use 'logistic' or 'lda').")


def _select_C(X_tr, y_tr, groups_tr, model_name, seed):
    """Pick C by inner subject-grouped CV on the training subjects only (logistic only)."""
    if model_name != "logistic":
        return None
    n_groups = len(np.unique(groups_tr))
    n_splits = min(5, n_groups)
    gkf = GroupKFold(n_splits=n_splits)
    best_C, best_score = C_GRID[0], -np.inf
    for C in C_GRID:
        scores = []
        for itr, ite in gkf.split(X_tr, y_tr, groups_tr):
            scaler = StandardScaler().fit(X_tr[itr])
            clf = _make_model(model_name, C).fit(scaler.transform(X_tr[itr]), y_tr[itr])
            pred = clf.predict(scaler.transform(X_tr[ite]))
            scores.append(balanced_accuracy_score(y_tr[ite], pred))
        m = float(np.mean(scores))
        if m > best_score:
            best_score, best_C = m, C
    return best_C


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bundle", required=True, help="feature_bundle.npz path.")
    ap.add_argument("--out-dir", default="outputs/decoding", help="Output directory.")
    ap.add_argument("--model", choices=["logistic", "lda"], default="logistic")
    ap.add_argument("--feature-family", choices=["band_power", "covariance", "all"],
                    default="band_power")
    ap.add_argument("--channel-set", choices=["all", "brain"], default="all",
                    help="'all'=8-ch headline montage; 'brain'=6-ch A1/A2-excluded diagnostic.")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    np.random.seed(args.seed)
    bundle = np.load(args.bundle, allow_pickle=True)

    X_all = bundle["X_signal"]
    y = bundle["y"].astype(int)
    subject_id = bundle["subject_id"].astype(str)
    session_id = bundle["session_id"].astype(str)
    trial_id = bundle["trial_id"].astype(str)
    cols, kept_channels = _select_columns(bundle, args.feature_family, args.channel_set)
    X = X_all[:, cols]
    is_headline = (args.channel_set == "all")

    tag = f"{args.model}_{args.feature_family}_{args.channel_set}"
    print(f"Decoder run: {tag}")
    print(f"  features: {X.shape[1]} cols ({args.feature_family}), channels: {kept_channels}")
    print(f"  {'HEADLINE' if is_headline else 'DIAGNOSTIC (A1/A2 excluded)'}\n")

    subjects = sorted(np.unique(subject_id).tolist())
    pred_rows = []
    per_subject = []
    for held in subjects:
        te = subject_id == held
        tr = ~te
        groups_tr = subject_id[tr]
        C = _select_C(X[tr], y[tr], groups_tr, args.model, args.seed)
        scaler = StandardScaler().fit(X[tr])
        clf = _make_model(args.model, C if C is not None else 1.0)
        clf.fit(scaler.transform(X[tr]), y[tr])
        Xte = scaler.transform(X[te])
        pred = clf.predict(Xte)
        if hasattr(clf, "predict_proba"):
            score = clf.predict_proba(Xte)[:, 1]
        else:
            score = clf.decision_function(Xte)
        ba = balanced_accuracy_score(y[te], pred)
        per_subject.append({"subject_id": held, "n_test": int(te.sum()),
                            "selected_C": C, "signal_ba": float(ba)})
        # One prediction row per held-out trial (dashboard input contract; Codex adds
        # the control columns from the same folds).
        for n, k in enumerate(np.where(te)[0]):
            pred_rows.append({
                "subject_id": subject_id[k], "session_id": session_id[k],
                "trial_id": trial_id[k], "load_binary": int(y[k]),
                "signal_pred": int(pred[n]), "signal_score": float(score[n]),
            })
        print(f"  {held}: balanced acc = {ba:.3f}  (n_test={int(te.sum())}, C={C})")

    per_df = pd.DataFrame(per_subject)
    mean_ba = float(per_df["signal_ba"].mean())
    pred_df = pd.DataFrame(pred_rows)

    pred_path = os.path.join(args.out_dir, f"predictions_{tag}.csv")
    sub_path = os.path.join(args.out_dir, f"subject_scores_{tag}.csv")
    pred_df.to_csv(pred_path, index=False)
    per_df.to_csv(sub_path, index=False)
    with open(os.path.join(args.out_dir, f"summary_{tag}.json"), "w") as fh:
        json.dump({
            "config": {"model": args.model, "feature_family": args.feature_family,
                       "channel_set": args.channel_set, "is_headline": is_headline,
                       "channels": kept_channels, "n_features": int(X.shape[1]),
                       "seed": args.seed, "C_grid": C_GRID},
            "mean_signal_balanced_accuracy": mean_ba,
            "per_subject": per_subject,
        }, fh, indent=2)

    print(f"\nMean LOSO balanced accuracy ({tag}): {mean_ba:.3f}")
    print(f"  (signal side only; subtract Codex's strongest control for the +0.075 test)")
    print(f"Wrote:\n  {pred_path}\n  {sub_path}")


if __name__ == "__main__":
    main()
