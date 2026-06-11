"""Build the project-wide trial metadata table from all NIX session files.

Reads per-trial task metadata from every Data_Subject_*_Session_*.h5 file (cheap:
no voltage arrays are loaded) and writes one tidy table with one row per trial. This
table is the shared contract between Claude's data layer and Codex's controls /
statistics / dashboard lane: it carries the LOSO grouping keys, the primary target,
the behavioral/timing covariates, the event onsets that define the maintenance window,
and explicit exclusion flags -- so the controls harness can enforce the Claim Sheet
(forbidden inputs, leakage guards) instead of reconstructing structure ad hoc later.

Columns flagged FORBIDDEN-FOR-CONTROLS (set_size, load_binary) must never enter the
behavioral-only or timing-only controls; that rule is documented here and enforced
downstream by Codex's harness.

Usage:
    .\\venv\\Scripts\\python.exe scripts\\build_trial_metadata.py \\
        --data-dir "D:\\Simultaneous EEG_LFP\\data_nix" --out-dir outputs
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict

import pandas as pd

sys.path.insert(0, __file__.rsplit("scripts", 1)[0])

from utils import nix_io

# Columns that encode the decoding target and are forbidden in behavioral/timing controls.
FORBIDDEN_FOR_CONTROLS = ["set_size", "load_binary"]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", required=True,
                    help="Path to the dataset's data_nix/ directory.")
    ap.add_argument("--out-dir", default="outputs",
                    help="Directory for output tables (default: outputs).")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    files = nix_io.list_session_files(args.data_dir)
    print(f"Found {len(files)} session files in {args.data_dir}")

    rows = []
    session_summary = []
    for i, path in enumerate(files, 1):
        meta = nix_io.read_session_metadata(path)
        print(f"  [{i:2d}/{len(files)}] {meta.subject_id}/{meta.session_id}: "
              f"{len(meta.trials)} trials, {len(meta.scalp_channels)} scalp ch, "
              f"{meta.n_ieeg_channels} iEEG ch, {meta.n_units} units")
        for t in meta.trials:
            d = asdict(t)
            # maintenance ends at probe onset; expose explicitly for windowing/controls.
            d["maintenance_offset_s"] = t.probe_onset_s
            d["scalp_sample_rate_hz"] = meta.scalp_sample_rate_hz
            d["ieeg_sample_rate_hz"] = meta.ieeg_sample_rate_hz
            d["n_scalp_channels"] = len(meta.scalp_channels)
            d["n_ieeg_channels"] = meta.n_ieeg_channels
            d["n_units"] = meta.n_units
            # Trial-level quality flag: dataset's per-trial artifact marker.
            d["trial_rejected"] = bool(t.artifact)
            d["rejection_reason"] = "artifact" if t.artifact else ""
            rows.append(d)
        session_summary.append({
            "subject_id": meta.subject_id,
            "session_id": meta.session_id,
            "n_trials": len(meta.trials),
            "n_scalp_channels": len(meta.scalp_channels),
            "n_ieeg_channels": meta.n_ieeg_channels,
            "n_units": meta.n_units,
            "scalp_channels": "|".join(meta.scalp_channels),
        })

    df = pd.DataFrame(rows)
    # Stable, readable column order.
    lead = ["subject_id", "session_id", "trial_id", "trial_index",
            "set_size", "load_binary",
            "match", "correct", "response", "response_time_s",
            "previous_trial_correct", "probe_letter",
            "fixation_onset_s", "encoding_onset_s", "maintenance_onset_s",
            "maintenance_offset_s", "probe_onset_s", "response_onset_s",
            "scalp_sample_rate_hz", "ieeg_sample_rate_hz",
            "n_scalp_channels", "n_ieeg_channels", "n_units",
            "artifact", "trial_rejected", "rejection_reason"]
    df = df[[c for c in lead if c in df.columns] + [c for c in df.columns if c not in lead]]
    df = df.sort_values(["subject_id", "session_id", "trial_index"]).reset_index(drop=True)

    csv_path = os.path.join(args.out_dir, "trial_metadata.csv")
    pq_path = os.path.join(args.out_dir, "trial_metadata.parquet")
    df.to_csv(csv_path, index=False)
    df.to_parquet(pq_path, index=False)

    sess_df = pd.DataFrame(session_summary).sort_values(["subject_id", "session_id"])
    sess_csv = os.path.join(args.out_dir, "session_summary.csv")
    sess_df.to_csv(sess_csv, index=False)

    # Montage sidecar (record whether scalp labels are constant across sessions).
    montages = sess_df["scalp_channels"].unique()
    montage_consistent = len(montages) == 1
    with open(os.path.join(args.out_dir, "scalp_montage.json"), "w") as fh:
        json.dump({
            "consistent_across_sessions": bool(montage_consistent),
            "channels": montages[0].split("|") if montage_consistent else
                        {row["subject_id"] + "/" + row["session_id"]: row["scalp_channels"].split("|")
                         for _, row in sess_df.iterrows()},
        }, fh, indent=2)

    print(f"\nWrote {len(df)} trial rows:")
    print(f"  {csv_path}")
    print(f"  {pq_path}")
    print(f"  {sess_csv}")
    print(f"  {os.path.join(args.out_dir, 'scalp_montage.json')}")
    print(f"\nForbidden-for-controls columns (target encoders): {FORBIDDEN_FOR_CONTROLS}")
    print(f"Scalp montage consistent across all sessions: {montage_consistent}")
    if not montage_consistent:
        print("  WARNING: scalp montage differs between sessions; see scalp_montage.json")


if __name__ == "__main__":
    main()
