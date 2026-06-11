"""Mechanism gate: audit per-subject medial-temporal-lobe (MTL) electrode coverage.

The mechanism (half B) analysis asks whether the scalp-decoded load signature is
coupled to directly recorded deep MTL activity. That analysis is only meaningful for
subjects whose implant actually sampled the MTL, so the Claim Sheet predeclares a gate:
the mechanism analysis proceeds only if at least 5 subjects have adequate MTL coverage.
This script computes that coverage from the iEEG electrode anatomy shipped in each NIX
session file and reports, per subject, how many contacts fall in MTL structures.

What counts as MTL here: the medial-temporal core targeted by this dataset's depth
electrodes -- hippocampus (``Hipp``), amygdala (``Amyg``), and parahippocampal gyrus
(``PhG``, which carries the entorhinal/perirhinal/parahippocampal cortices). Lateral and
ventral temporal neocortex (middle/superior/inferior temporal gyri, fusiform) and other
regions (insula, parietal) are reported as ``non_mtl`` and do not count toward the gate.
Unlabeled contacts (``no_label_found``) are reported separately and never counted as MTL.

A subject's contacts are unioned across that subject's sessions by contact label, because
the implant is fixed within a subject; a labeled anatomy always wins over an unlabeled
reading of the same contact. ``adequate_mtl_coverage`` is True when the subject has at
least ``--min-mtl-contacts`` MTL contacts (default 2) including at least one hippocampal
or amygdalar contact, since those are the canonical deep targets for a coupling readout.

Outputs (under ``--out-dir``, default ``outputs/mechanism``):
  * ``mtl_coverage.csv``        -- one row per subject with per-region counts and the gate.
  * ``mtl_contacts.csv``        -- one row per MTL contact (subject, contact, region, MNI).
  * ``mtl_coverage_summary.json`` -- the gate decision and the qualifying-subject list.

Usage:
    .\\venv\\Scripts\\python.exe scripts\\audit_mtl_coverage.py \\
        --data-dir "D:\\Simultaneous EEG_LFP\\data_nix" --out-dir outputs\\mechanism
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import nix_io  # noqa: E402

# Anatomy region-code prefixes (the token before the first comma) that are MTL core.
MTL_REGIONS = {
    "Hipp": "hippocampus",
    "Amyg": "amygdala",
    "PhG": "parahippocampal",
}
# The canonical deep targets a coupling readout needs at least one of.
DEEP_MTL = {"hippocampus", "amygdala"}


def _region_of(anatomy: str) -> tuple[str, str]:
    """Map a raw anatomy string to (mtl_subregion_or_none, coarse_class).

    Returns:
        (subregion, klass) where subregion is one of MTL_REGIONS.values() or '' and
        klass is 'mtl', 'non_mtl', or 'unlabeled'.
    """
    if anatomy == "no_label_found" or not anatomy:
        return "", "unlabeled"
    prefix = anatomy.split(",")[0].strip()
    if prefix in MTL_REGIONS:
        return MTL_REGIONS[prefix], "mtl"
    return "", "non_mtl"


def _hemisphere_of(anatomy: str) -> str:
    """Best-effort hemisphere from the anatomy string ('left'/'right'/'unknown')."""
    a = anatomy.lower()
    if "left" in a:
        return "left"
    if "right" in a:
        return "right"
    return "unknown"


def _subject_label(path: str) -> str:
    """Map a session filename to a subject id like 'S01'."""
    m = nix_io._FNAME_RE.search(os.path.basename(path))
    if not m:
        raise ValueError(f"Cannot parse subject id from {path}")
    return f"S{int(m.group(1)):02d}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", required=True, help="Directory of Data_Subject_*.h5 files.")
    ap.add_argument("--out-dir", default="outputs/mechanism", help="Output directory.")
    ap.add_argument("--min-mtl-contacts", type=int, default=2,
                    help="Minimum MTL contacts for adequate coverage (default 2).")
    ap.add_argument("--min-adequate-subjects", type=int, default=5,
                    help="Gate threshold on the number of adequately covered subjects.")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    files = nix_io.list_session_files(args.data_dir)

    # Union contacts per subject across sessions (labeled anatomy wins over unlabeled).
    per_subject_contacts: dict[str, dict[str, dict]] = defaultdict(dict)
    sessions_per_subject: dict[str, int] = defaultdict(int)
    for path in files:
        subj = _subject_label(path)
        sessions_per_subject[subj] += 1
        for rec in nix_io.read_ieeg_electrode_info(path):
            ch = rec["channel"]
            existing = per_subject_contacts[subj].get(ch)
            if existing is None or (existing["anatomy"] == "no_label_found"
                                    and rec["anatomy"] != "no_label_found"):
                per_subject_contacts[subj][ch] = rec

    subject_rows = []
    contact_rows = []
    for subj in sorted(per_subject_contacts):
        contacts = per_subject_contacts[subj]
        region_counts = defaultdict(int)
        hemi_counts = defaultdict(int)
        n_mtl = n_unlabeled = n_non_mtl = 0
        for ch, rec in contacts.items():
            subregion, klass = _region_of(rec["anatomy"])
            if klass == "mtl":
                n_mtl += 1
                region_counts[subregion] += 1
                hemi_counts[_hemisphere_of(rec["anatomy"])] += 1
                contact_rows.append({
                    "subject_id": subj, "contact": ch, "mtl_subregion": subregion,
                    "hemisphere": _hemisphere_of(rec["anatomy"]),
                    "anatomy": rec["anatomy"], "mni_xyz": rec["mni_xyz"],
                })
            elif klass == "unlabeled":
                n_unlabeled += 1
            else:
                n_non_mtl += 1

        has_deep = any(region_counts.get(r, 0) > 0 for r in DEEP_MTL)
        adequate = (n_mtl >= args.min_mtl_contacts) and has_deep
        subject_rows.append({
            "subject_id": subj,
            "n_sessions": sessions_per_subject[subj],
            "n_contacts": len(contacts),
            "n_mtl": n_mtl,
            "n_hippocampus": region_counts.get("hippocampus", 0),
            "n_amygdala": region_counts.get("amygdala", 0),
            "n_parahippocampal": region_counts.get("parahippocampal", 0),
            "mtl_left": hemi_counts.get("left", 0),
            "mtl_right": hemi_counts.get("right", 0),
            "n_non_mtl": n_non_mtl,
            "n_unlabeled": n_unlabeled,
            "has_deep_target": has_deep,
            "adequate_mtl_coverage": adequate,
        })

    subjects_df = pd.DataFrame(subject_rows)
    contacts_df = pd.DataFrame(contact_rows)
    n_adequate = int(subjects_df["adequate_mtl_coverage"].sum())
    gate_pass = n_adequate >= args.min_adequate_subjects
    qualifying = subjects_df.loc[subjects_df["adequate_mtl_coverage"], "subject_id"].tolist()

    cov_path = os.path.join(args.out_dir, "mtl_coverage.csv")
    contacts_path = os.path.join(args.out_dir, "mtl_contacts.csv")
    summary_path = os.path.join(args.out_dir, "mtl_coverage_summary.json")
    subjects_df.to_csv(cov_path, index=False)
    contacts_df.to_csv(contacts_path, index=False)
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump({
            "n_subjects": int(len(subjects_df)),
            "n_adequate_subjects": n_adequate,
            "min_mtl_contacts": args.min_mtl_contacts,
            "min_adequate_subjects": args.min_adequate_subjects,
            "mechanism_gate_pass": bool(gate_pass),
            "qualifying_subjects": qualifying,
            "mtl_definition": MTL_REGIONS,
            "deep_target_required_one_of": sorted(DEEP_MTL),
        }, fh, indent=2)

    print("MTL coverage audit")
    print(subjects_df.to_string(index=False))
    print(f"\nAdequate-coverage subjects (>= {args.min_mtl_contacts} MTL contacts incl. "
          f"hippocampus/amygdala): {n_adequate}/{len(subjects_df)} -> {qualifying}")
    print(f"Mechanism gate (>= {args.min_adequate_subjects} subjects): "
          f"{'PASS' if gate_pass else 'FAIL'}")
    print(f"\nWrote:\n  {cov_path}\n  {contacts_path}\n  {summary_path}")


if __name__ == "__main__":
    main()
