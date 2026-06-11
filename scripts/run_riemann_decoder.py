"""Signal model rungs 2-3: Riemannian load decoder under LOSO.

This climbs the pre-registered model ladder past the rung-1 logistic/LDA baseline by
treating each trial's per-band channel covariance as a point on the manifold of
symmetric positive-definite (SPD) matrices instead of as a flat vector. The covariances
themselves are the ones already shipped in the feature bundle (``cov_matrices``), shrunk
toward a scaled identity at feature-build time. Two methods are exposed:

  * ``tangent`` (rung 2 -- filter-bank tangent space + shrinkage). For each frequency
    band, the Riemannian (geometric) mean of the TRAINING covariances is computed and
    used to whiten and project every trial's covariance into a Euclidean tangent space.
    Per-band tangent vectors are concatenated and fed to a regularized logistic model.
    This differs from rung 1's covariance features, which referenced the identity matrix
    rather than the data's own geometric center; referencing the training mean is the
    standard Riemannian classification pipeline.
  * ``mdm`` (rung 3 -- minimum distance to Riemannian mean). For each band, a Riemannian
    mean is computed per class on the TRAINING covariances; a test covariance is labeled
    by the nearest class mean under the affine-invariant distance, summed across bands.
    This is a fully geometric classifier with no Euclidean model on top.

Discipline (identical to rung 1, Claim Sheet + Codex controls spec):
  * Leave-one-subject-out: the held-out subject is touched once. The geometric means,
    the tangent reference, the standardizer, and (for ``tangent``) the logistic C are all
    fit on the training subjects only; the held-out subject is scored a single time.
  * Balanced accuracy is the metric (classes are ~2:1 by construction).
  * The output is the signal side only, in the same file contract as
    ``run_load_decoder.py`` so Codex's control / statistics / dashboard scripts consume
    these rungs unchanged (run them with ``--feature-family covariance``).

Two predeclared channel sets (``--channel-set``), matching rung 1:
  * ``all``   -- the locked 8-channel common montage (HEADLINE).
  * ``brain`` -- the 6 brain channels, excluding A1/A2 references (SENSITIVITY
                 DIAGNOSTIC; it cannot move the success bar).

Usage:
    .\\venv\\Scripts\\python.exe scripts\\run_riemann_decoder.py \\
        --bundle outputs\\features\\feature_bundle.npz --out-dir outputs\\decoding \\
        --method tangent --channel-set all
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler

# Make the project-root utils importable when run as a script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import riemann as R  # noqa: E402

# Inner-CV grid for the logistic regularization strength (tangent method only).
C_GRID = [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0]


def _brain_channel_indices(channel_names, channel_role):
    """Return covariance-axis indices of the brain channels (A1/A2 references dropped)."""
    return np.array(
        [i for i, r in enumerate(channel_role) if r == "brain"], dtype=int
    )


def _subselect_channels(covs: np.ndarray, idx: np.ndarray) -> np.ndarray:
    """Restrict a (n, n_bands, k, k) covariance stack to a channel index subset."""
    return covs[:, :, idx][:, :, :, idx]


def _recenter_by_subject(covs: np.ndarray, subject_id: np.ndarray) -> np.ndarray:
    """Unsupervised Riemannian recentering: whiten each subject by their own mean.

    For every subject and band, the Riemannian mean of that subject's covariances is
    computed from the covariances alone (no labels) and used to whiten them, so each
    subject's covariances are centered at the identity. This removes the subject-specific
    offset that otherwise dominates cross-subject affine-invariant distances (Zanini et
    al., 2018, "Transfer Learning: A Riemannian Geometry Framework..."). It is a
    transductive step that uses held-out *inputs* but never held-out *labels*, so it does
    not leak the decoding target.

    Args:
        covs: (n, n_bands, k, k) SPD covariances.
        subject_id: (n,) subject label per trial.

    Returns:
        (n, n_bands, k, k) recentered covariances.
    """
    out = np.empty_like(covs)
    n_bands = covs.shape[1]
    for s in np.unique(subject_id):
        sel = subject_id == s
        for b in range(n_bands):
            mean_sb = R.riemannian_mean(covs[sel, b])
            w = R.spd_invsqrt(mean_sb[None])[0]
            out[sel, b] = w @ covs[sel, b] @ w
    return out


def _tangent_features(covs_tr, covs_te):
    """Filter-bank tangent-space features referenced to per-band TRAIN geometric means.

    Args:
        covs_tr: (n_tr, n_bands, k, k) regularized SPD training covariances.
        covs_te: (n_te, n_bands, k, k) regularized SPD held-out covariances.

    Returns:
        (X_tr, X_te) tangent-space feature matrices, bands concatenated.
    """
    n_bands = covs_tr.shape[1]
    tr_parts, te_parts = [], []
    for b in range(n_bands):
        ref = R.riemannian_mean(covs_tr[:, b])      # fit on training covariances only
        tr_parts.append(R.tangent_space(covs_tr[:, b], ref))
        te_parts.append(R.tangent_space(covs_te[:, b], ref))
    return np.concatenate(tr_parts, axis=1), np.concatenate(te_parts, axis=1)


def _select_C(X_tr, y_tr, groups_tr, seed):
    """Pick logistic C by inner subject-grouped CV on the training subjects only."""
    n_splits = min(5, len(np.unique(groups_tr)))
    gkf = GroupKFold(n_splits=n_splits)
    best_C, best_score = C_GRID[0], -np.inf
    for C in C_GRID:
        scores = []
        for itr, ite in gkf.split(X_tr, y_tr, groups_tr):
            scaler = StandardScaler().fit(X_tr[itr])
            clf = LogisticRegression(C=C, solver="liblinear", max_iter=2000)
            clf.fit(scaler.transform(X_tr[itr]), y_tr[itr])
            pred = clf.predict(scaler.transform(X_tr[ite]))
            scores.append(balanced_accuracy_score(y_tr[ite], pred))
        m = float(np.mean(scores))
        if m > best_score:
            best_score, best_C = m, C
    return best_C


def _fit_predict_tangent(covs_tr, y_tr, groups_tr, covs_te, seed):
    """Rung 2: tangent-space projection + regularized logistic. Returns (pred, score, C)."""
    X_tr, X_te = _tangent_features(covs_tr, covs_te)
    C = _select_C(X_tr, y_tr, groups_tr, seed)
    scaler = StandardScaler().fit(X_tr)
    clf = LogisticRegression(C=C, solver="liblinear", max_iter=2000)
    clf.fit(scaler.transform(X_tr), y_tr)
    Xte = scaler.transform(X_te)
    return clf.predict(Xte), clf.predict_proba(Xte)[:, 1], C


def _fit_predict_mdm(covs_tr, y_tr, covs_te):
    """Rung 3: minimum distance to per-class Riemannian means. Returns (pred, score, None).

    Score is d(class 0 mean) - d(class 1 mean) summed across bands: larger => closer to
    the high-load class mean.
    """
    classes = np.array([0, 1])
    n_bands = covs_tr.shape[1]
    class_means = {c: [R.riemannian_mean(covs_tr[y_tr == c, b]) for b in range(n_bands)]
                   for c in classes}
    n_te = covs_te.shape[0]
    dist = {c: np.zeros(n_te) for c in classes}
    for c in classes:
        for b in range(n_bands):
            mean_b = class_means[c][b]
            for i in range(n_te):
                dist[c][i] += R.airm_distance(mean_b, covs_te[i, b])
    pred = np.where(dist[1] < dist[0], 1, 0)
    score = dist[0] - dist[1]
    return pred, score, None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bundle", required=True, help="feature_bundle.npz path.")
    ap.add_argument("--out-dir", default="outputs/decoding", help="Output directory.")
    ap.add_argument("--method", choices=["tangent", "mdm"], required=True,
                    help="'tangent'=rung 2 filter-bank tangent space; 'mdm'=rung 3.")
    ap.add_argument("--channel-set", choices=["all", "brain"], default="all",
                    help="'all'=8-ch headline montage; 'brain'=6-ch A1/A2-excluded diagnostic.")
    ap.add_argument("--ridge", type=float, default=1e-6,
                    help="Trace-proportional SPD ridge restoring strict PD after float32.")
    ap.add_argument("--recenter", action="store_true",
                    help="Unsupervised per-subject Riemannian recentering (label-free "
                         "domain alignment). Tags the run with an 'rc' suffix.")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    np.random.seed(args.seed)
    bundle = np.load(args.bundle, allow_pickle=True)

    covs = bundle["cov_matrices"].astype(np.float64)  # (n, n_bands, k, k)
    y = bundle["y"].astype(int)
    subject_id = bundle["subject_id"].astype(str)
    session_id = bundle["session_id"].astype(str)
    trial_id = bundle["trial_id"].astype(str)
    channel_names = list(bundle["channel_names"].astype(str))
    channel_role = list(bundle["channel_role"].astype(str))

    channel_names = [str(c) for c in channel_names]
    channel_role = [str(r) for r in channel_role]
    if args.channel_set == "brain":
        idx = _brain_channel_indices(channel_names, channel_role)
        covs = _subselect_channels(covs, idx)
        kept_channels = [channel_names[i] for i in idx]
    else:
        kept_channels = list(channel_names)
    covs = R.regularize_spd(covs, ridge=args.ridge)  # strict SPD for the geometry
    if args.recenter:
        covs = _recenter_by_subject(covs, subject_id)
    is_headline = (args.channel_set == "all")

    method_tag = f"{args.method}rc" if args.recenter else args.method
    tag = f"{method_tag}_cov_{args.channel_set}"
    print(f"Riemannian decoder run: {tag}")
    print(f"  method: {args.method}; channels: {kept_channels}; bands: {covs.shape[1]}")
    print(f"  {'HEADLINE' if is_headline else 'DIAGNOSTIC (A1/A2 excluded)'}\n")

    subjects = sorted(np.unique(subject_id).tolist())
    pred_rows = []
    per_subject = []
    for held in subjects:
        te = subject_id == held
        tr = ~te
        covs_tr, covs_te = covs[tr], covs[te]
        y_tr = y[tr]
        if args.method == "tangent":
            pred, score, C = _fit_predict_tangent(
                covs_tr, y_tr, subject_id[tr], covs_te, args.seed)
        else:
            pred, score, C = _fit_predict_mdm(covs_tr, y_tr, covs_te)
        ba = balanced_accuracy_score(y[te], pred)
        per_subject.append({"subject_id": held, "n_test": int(te.sum()),
                            "selected_C": C, "signal_ba": float(ba)})
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
            "config": {"method": args.method, "channel_set": args.channel_set,
                       "recenter": bool(args.recenter), "is_headline": is_headline,
                       "channels": kept_channels, "n_bands": int(covs.shape[1]),
                       "ridge": args.ridge, "seed": args.seed, "C_grid": C_GRID},
            "mean_signal_balanced_accuracy": mean_ba,
            "per_subject": per_subject,
        }, fh, indent=2)

    print(f"\nMean LOSO balanced accuracy ({tag}): {mean_ba:.3f}")
    print(f"  (signal side only; subtract Codex's strongest control for the +0.075 test)")
    print(f"Wrote:\n  {pred_path}\n  {sub_path}")


if __name__ == "__main__":
    main()
