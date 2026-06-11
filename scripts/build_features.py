"""Build the scalp-only feature bundle for the headline load-decoding analysis.

Reads aligned scalp epochs for every session, restricts them to the locked common
montage (the 8 channels present in all 9 subjects), computes maintenance-window
features (band power + tangent-space covariance), and writes a single serialized
bundle that is the contract between Claude's signal pipeline and Codex's controls /
statistics / dashboard lane.

The bundle is deliberately scalp-only: it contains no behavioral or timing columns in
``X_signal`` (those live in ``feature_metadata`` for Codex's controls to build their
own forbidden-input-checked matrices). Artifact-rejected trials are dropped and listed
in ``exclusions.csv`` -- no silent exclusions.

Locked configuration enforced here (see agents/Codex/Phase 2 Controls and Statistics
Spec.md): common physical montage only, no missing-channel padding/imputation, channel
role preserved so A1/A2 (ear/mastoid references) can be excluded in the predeclared
brain-only sensitivity diagnostic.

Usage:
    .\\venv\\Scripts\\python.exe scripts\\build_features.py \\
        --data-dir "D:\\Simultaneous EEG_LFP\\data_nix" \\
        --metadata outputs\\trial_metadata.csv \\
        --montage outputs\\montage_intersection.json \\
        --out-dir outputs\\features
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, __file__.rsplit("scripts", 1)[0])

from utils import nix_io
from utils.epoching import MAINTENANCE_WINDOW_S
from utils.features import BANDS, compute_features

# Ear/mastoid reference channels in the common montage (role-tagged, not brain).
REFERENCE_CHANNELS = {"A1", "A2"}


def _channel_indices(session_channels: list[str], montage: list[str], path: str) -> list[int]:
    """Return indices of the common-montage channels within a session's channel list.

    Fails loudly if any locked-montage channel is missing from the session, since the
    headline run forbids padding/imputation for absent channels.
    """
    idx = []
    for ch in montage:
        if ch not in session_channels:
            raise ValueError(
                f"{path}: locked montage channel '{ch}' absent from session channels "
                f"{session_channels}. Padding/imputation is forbidden for the headline run."
            )
        idx.append(session_channels.index(ch))
    return idx


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", required=True,
                    help="Path to the dataset's data_nix/ directory.")
    ap.add_argument("--metadata", required=True,
                    help="Path to trial_metadata.csv (from build_trial_metadata.py).")
    ap.add_argument("--montage", required=True,
                    help="Path to montage_intersection.json (common-montage definition).")
    ap.add_argument("--out-dir", default="outputs/features",
                    help="Directory for the feature bundle (default: outputs/features).")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    with open(args.montage) as fh:
        montage_info = json.load(fh)
    montage = list(montage_info["common_intersection"])
    print(f"Locked common montage ({len(montage)} ch): {montage}")

    meta = pd.read_csv(args.metadata)
    meta = meta.set_index("trial_id", drop=False)
    print(f"Loaded {len(meta)} trial metadata rows from {args.metadata}")

    files = nix_io.list_session_files(args.data_dir)
    print(f"Found {len(files)} session files\n")

    X_blocks: list[np.ndarray] = []
    cov_blocks: list[np.ndarray] = []
    kept_trial_ids: list[str] = []
    exclusions: list[dict] = []
    feature_names = feature_family = band_names = None

    for i, path in enumerate(files, 1):
        epochs = nix_io.load_scalp_epochs(path)
        ch_idx = _channel_indices(epochs.channels, montage, path)
        sub = epochs.data[:, ch_idx, :]  # (n_trials, 8, n_samples), montage order
        fb = compute_features(
            full_epochs=sub,
            offset_s=epochs.offset_s,
            fs=epochs.sample_rate_hz,
            channel_names=montage,
            window_s=MAINTENANCE_WINDOW_S,
            bands=BANDS,
        )
        if feature_names is None:
            feature_names = fb.feature_names
            feature_family = fb.feature_family
            band_names = fb.band_names

        # Keep non-artifact trials with a valid binary label; record drops.
        n_kept = 0
        for k, tid in enumerate(epochs.trial_ids):
            if tid not in meta.index:
                exclusions.append({"trial_id": tid, "subject_id": epochs.subject_id,
                                   "session_id": epochs.session_id, "reason": "no_metadata_row"})
                continue
            row = meta.loc[tid]
            if bool(row["trial_rejected"]):
                exclusions.append({"trial_id": tid, "subject_id": epochs.subject_id,
                                   "session_id": epochs.session_id,
                                   "reason": str(row["rejection_reason"]) or "artifact"})
                continue
            X_blocks.append(fb.X[k])
            cov_blocks.append(fb.cov_matrices[k])
            kept_trial_ids.append(tid)
            n_kept += 1
        print(f"  [{i:2d}/{len(files)}] {epochs.subject_id}/{epochs.session_id}: "
              f"{n_kept}/{len(epochs.trial_ids)} trials kept")

    X = np.asarray(X_blocks, dtype=np.float32)
    cov_matrices = np.asarray(cov_blocks, dtype=np.float32)
    meta_kept = meta.loc[kept_trial_ids].reset_index(drop=True)
    y = meta_kept["load_binary"].to_numpy(dtype=np.int64)
    subject_id = meta_kept["subject_id"].to_numpy(dtype=object)
    session_id = meta_kept["session_id"].to_numpy(dtype=object)
    trial_id = meta_kept["trial_id"].to_numpy(dtype=object)

    channel_role = ["reference" if ch in REFERENCE_CHANNELS else "brain" for ch in montage]
    band_low = np.array([BANDS[b][0] for b in band_names], dtype=np.float64)
    band_high = np.array([BANDS[b][1] for b in band_names], dtype=np.float64)

    # --- Serialize the bundle (npz arrays + sidecar tables). ---
    npz_path = os.path.join(args.out_dir, "feature_bundle.npz")
    np.savez_compressed(
        npz_path,
        X_signal=X,
        y=y,
        subject_id=subject_id,
        session_id=session_id,
        trial_id=trial_id,
        feature_names=np.array(feature_names, dtype=object),
        feature_family=np.array(feature_family, dtype=object),
        channel_names=np.array(montage, dtype=object),
        channel_role=np.array(channel_role, dtype=object),
        band_names=np.array(band_names, dtype=object),
        band_low_hz=band_low,
        band_high_hz=band_high,
        cov_matrices=cov_matrices,
        window_s=np.array(MAINTENANCE_WINDOW_S, dtype=np.float64),
    )

    # Metadata table (Codex's controls build their own X from these covariates).
    meta_path = os.path.join(args.out_dir, "feature_metadata.parquet")
    meta_csv = os.path.join(args.out_dir, "feature_metadata.csv")
    meta_kept.to_parquet(meta_path, index=False)
    meta_kept.to_csv(meta_csv, index=False)

    # Exclusions table (machine-readable; mirrors the human-readable counts below).
    excl_df = pd.DataFrame(exclusions, columns=["trial_id", "subject_id", "session_id", "reason"])
    excl_path = os.path.join(args.out_dir, "exclusions.csv")
    excl_df.to_csv(excl_path, index=False)

    # Feature dictionary sidecar (human-auditable column provenance).
    fam_counts = {fam: int(np.sum(np.array(feature_family) == fam))
                  for fam in sorted(set(feature_family))}
    with open(os.path.join(args.out_dir, "feature_names.json"), "w") as fh:
        json.dump({
            "n_features": len(feature_names),
            "feature_family_counts": fam_counts,
            "channel_names": montage,
            "channel_role": dict(zip(montage, channel_role)),
            "band_names": band_names,
            "band_edges_hz": {b: list(BANDS[b]) for b in band_names},
            "window_s": list(MAINTENANCE_WINDOW_S),
            "feature_names": feature_names,
            "feature_family": feature_family,
        }, fh, indent=2)

    print(f"\nWrote feature bundle:")
    print(f"  {npz_path}")
    print(f"  X_signal: {X.shape} ({fam_counts})")
    print(f"  cov_matrices: {cov_matrices.shape}")
    print(f"  {meta_path}")
    print(f"  {excl_path}  ({len(excl_df)} dropped trials)")
    print(f"  included trials: {len(y)}  (class balance: "
          f"low={int(np.sum(y == 0))}, high={int(np.sum(y == 1))})")
    print(f"  subjects: {sorted(set(subject_id.tolist()))}")


if __name__ == "__main__":
    main()
