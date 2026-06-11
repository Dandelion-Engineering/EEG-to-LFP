"""Emit and validate the leave-one-subject-out (LOSO) fold definitions.

The headline claim is a cross-subject generalization claim, so the evaluation is LOSO:
nine folds, each holding out one subject entirely while training on the other eight.
This script writes the canonical fold definitions once so that the signal model and all
of Codex's control models evaluate on *identical* folds, and it validates the two
leakage guards the Claim Sheet requires:

  * no subject appears in both the train and test side of any fold;
  * every analysis row maps to exactly one held-out fold (its own subject), and trial
    ids are unique (each trial is one maintenance window, so there is no multi-window
    leakage to police at this stage -- recorded explicitly so a future windowed variant
    re-checks it).

Usage:
    .\\venv\\Scripts\\python.exe scripts\\make_loso_splits.py \\
        --bundle outputs\\features\\feature_bundle.npz --out-dir outputs\\features
"""

from __future__ import annotations

import argparse
import json
import os

import numpy as np
import pandas as pd


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bundle", required=True,
                    help="Path to feature_bundle.npz (from build_features.py).")
    ap.add_argument("--out-dir", default="outputs/features",
                    help="Directory for fold definitions (default: outputs/features).")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    bundle = np.load(args.bundle, allow_pickle=True)
    subject_id = bundle["subject_id"].astype(str)
    session_id = bundle["session_id"].astype(str)
    trial_id = bundle["trial_id"].astype(str)
    y = bundle["y"].astype(int)

    if len(np.unique(trial_id)) != len(trial_id):
        raise ValueError("Duplicate trial_id in bundle: cannot define leak-free folds.")

    subjects = sorted(np.unique(subject_id).tolist())
    folds = []
    for fid, held in enumerate(subjects):
        test_mask = subject_id == held
        train_mask = ~test_mask
        train_subjects = sorted(np.unique(subject_id[train_mask]).tolist())
        # Guard: held-out subject must not leak into the training side.
        if held in train_subjects:
            raise ValueError(f"Fold {fid}: held-out subject {held} present in train set.")
        n_test = int(test_mask.sum())
        n_low = int(np.sum(y[test_mask] == 0))
        n_high = int(np.sum(y[test_mask] == 1))
        if n_low == 0 or n_high == 0:
            raise ValueError(
                f"Fold {fid} ({held}): held-out subject has an empty class "
                f"(low={n_low}, high={n_high}); balanced accuracy is undefined."
            )
        folds.append({
            "fold_id": fid,
            "held_out_subject": held,
            "n_train": int(train_mask.sum()),
            "n_test": n_test,
            "test_low": n_low,
            "test_high": n_high,
            "train_subjects": train_subjects,
        })

    # Per-trial fold assignment (each trial is test in exactly its own subject's fold).
    assign = pd.DataFrame({
        "trial_id": trial_id,
        "subject_id": subject_id,
        "session_id": session_id,
        "load_binary": y,
        "test_fold_subject": subject_id,  # held-out subject for which this trial is test
    })
    assign_path = os.path.join(args.out_dir, "loso_fold_assignment.csv")
    assign.to_csv(assign_path, index=False)

    folds_path = os.path.join(args.out_dir, "loso_folds.json")
    with open(folds_path, "w") as fh:
        json.dump({
            "scheme": "leave-one-subject-out",
            "grouping_key": "subject_id",
            "n_folds": len(folds),
            "n_trials": int(len(trial_id)),
            "windows_per_trial": 1,
            "folds": folds,
        }, fh, indent=2)

    print(f"LOSO: {len(folds)} folds over subjects {subjects}")
    for f in folds:
        print(f"  fold {f['fold_id']} hold-out {f['held_out_subject']}: "
              f"train n={f['n_train']} ({len(f['train_subjects'])} subj), "
              f"test n={f['n_test']} (low={f['test_low']}, high={f['test_high']})")
    print(f"\nWrote:\n  {folds_path}\n  {assign_path}")
    print("Leakage guards passed: no subject in train+test of any fold; trial ids unique.")


if __name__ == "__main__":
    main()
