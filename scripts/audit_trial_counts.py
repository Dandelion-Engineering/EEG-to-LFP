"""Pre-model trial-count (and montage) audit.

The Claim Sheet requires this audit to run BEFORE any decoder is fit, so the
predeclared +0.075 balanced-accuracy success bar is confirmed (or replaced by
agreement) against the real class counts rather than after seeing model results.

Consumes the trial metadata table from ``build_trial_metadata.py`` and reports, per
the controls spec:

    * included maintenance-period trials by subject / session / set size
    * included trials by subject and load_binary (low = set size 4; high = 6/8)
    * artifact-flagged (rejected) trials by subject / session
    * per-subject high/low class imbalance
    * Codex's discussion triggers (thin classes, imbalance, large exclusions)

It also audits the scalp montage across subjects -- which is NOT uniform in this
dataset -- and reports the common-channel intersection, because LOSO features must
live in a channel space shared by every held-out subject.

Outputs (to --out-dir):
    trial_count_audit.csv         per-subject machine-readable audit table
    trial_count_by_setsize.csv    subject x set-size counts
    montage_intersection.json     per-subject montage + common intersection
    trial_count_audit.md          human-readable summary with triggers

Usage:
    .\\venv\\Scripts\\python.exe scripts\\audit_trial_counts.py \\
        --metadata outputs\\trial_metadata.csv \\
        --montage outputs\\scalp_montage.json --out-dir outputs
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import pandas as pd

# Codex's discussion-trigger thresholds (from the controls spec).
MIN_PER_CLASS = 10          # fewer than this in either class -> trigger
MAX_CLASS_RATIO = 3.0       # high/low (or low/high) ratio above this -> trigger
MAX_EXCLUSION_FRAC = 0.20   # >20% primary exclusions for a subject -> trigger


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--metadata", required=True, help="trial_metadata.csv or .parquet")
    ap.add_argument("--montage", required=True, help="scalp_montage.json from build_trial_metadata.py")
    ap.add_argument("--out-dir", default="outputs", help="output directory (default: outputs)")
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    if args.metadata.endswith(".parquet"):
        df = pd.read_parquet(args.metadata)
    else:
        df = pd.read_csv(args.metadata)
    print(f"Loaded {len(df)} trial rows from {args.metadata}")

    # "Included" = not artifact-flagged. Maintenance window is identical for every
    # trial (verified), so every non-rejected trial contributes one maintenance epoch.
    df["included"] = ~df["trial_rejected"].astype(bool)

    # ---- Per-subject / set-size counts ----
    by_ss = (df[df["included"]]
             .groupby(["subject_id", "set_size"]).size()
             .unstack(fill_value=0).sort_index())
    by_ss.to_csv(os.path.join(args.out_dir, "trial_count_by_setsize.csv"))

    # ---- Per-subject audit ----
    rows = []
    for sub, g in df.groupby("subject_id"):
        inc = g[g["included"]]
        n_total = len(g)
        n_artifact = int((~g["included"]).sum())
        n_inc = len(inc)
        n_low = int((inc["load_binary"] == 0).sum())   # set size 4
        n_high = int((inc["load_binary"] == 1).sum())  # set sizes 6/8
        excl_frac = n_artifact / n_total if n_total else 0.0
        if n_low == 0 or n_high == 0:
            ratio = float("inf")
        else:
            ratio = max(n_low, n_high) / min(n_low, n_high)

        triggers = []
        if n_low == 0 or n_high == 0:
            triggers.append("empty_class")
        if n_low < MIN_PER_CLASS or n_high < MIN_PER_CLASS:
            triggers.append(f"thin_class(<{MIN_PER_CLASS})")
        if ratio > MAX_CLASS_RATIO:
            triggers.append(f"imbalance(>{MAX_CLASS_RATIO:.0f}:1)")
        if excl_frac > MAX_EXCLUSION_FRAC:
            triggers.append(f"exclusions(>{int(MAX_EXCLUSION_FRAC*100)}%)")

        rows.append({
            "subject_id": sub,
            "n_sessions": g["session_id"].nunique(),
            "n_trials_total": n_total,
            "n_artifact": n_artifact,
            "artifact_frac": round(excl_frac, 4),
            "n_included": n_inc,
            "n_low_ss4": n_low,
            "n_high_ss68": n_high,
            "high_low_ratio": round(ratio, 3) if ratio != float("inf") else "inf",
            "triggers": ";".join(triggers) if triggers else "",
        })
    audit = pd.DataFrame(rows).sort_values("subject_id")
    audit_csv = os.path.join(args.out_dir, "trial_count_audit.csv")
    audit.to_csv(audit_csv, index=False)

    # ---- Montage intersection ----
    with open(args.montage) as fh:
        montage = json.load(fh)
    if montage.get("consistent_across_sessions"):
        per_subject = {"ALL": montage["channels"]}
        common = set(montage["channels"])
    else:
        # channels is a {session_key: [labels]} dict; collapse to per-subject sets.
        per_sess = montage["channels"]
        per_subject = {}
        for key, labels in per_sess.items():
            sub = key.split("/")[0]
            per_subject.setdefault(sub, set()).update(labels)
        # A subject's channel set is the intersection across its own sessions...
        per_subject_sess = {}
        for key, labels in per_sess.items():
            sub = key.split("/")[0]
            per_subject_sess.setdefault(sub, []).append(set(labels))
        per_subject = {sub: set.intersection(*sets) for sub, sets in per_subject_sess.items()}
        common = set.intersection(*per_subject.values())

    common_sorted = sorted(common)
    brain_common = sorted(c for c in common if c not in ("A1", "A2"))
    montage_out = {
        "common_intersection": common_sorted,
        "n_common": len(common_sorted),
        "n_common_brain_excl_refs": len(brain_common),
        "common_brain_channels": brain_common,
        "per_subject_channels": {s: sorted(c) for s, c in sorted(per_subject.items())},
        "per_subject_channel_count": {s: len(c) for s, c in sorted(per_subject.items())},
    }
    with open(os.path.join(args.out_dir, "montage_intersection.json"), "w") as fh:
        json.dump(montage_out, fh, indent=2)

    # ---- Human-readable markdown ----
    n_with_triggers = int((audit["triggers"] != "").sum())
    lines = []
    lines.append("# Trial-Count and Montage Audit (pre-model gate)")
    lines.append("")
    lines.append(f"- Source metadata: `{os.path.basename(args.metadata)}` "
                 f"({len(df)} trial rows, {df['subject_id'].nunique()} subjects, "
                 f"{df['session_id'].nunique() if 'session_id' in df else '?'} session labels)")
    lines.append(f"- Inclusion rule: trial is included unless the dataset's per-trial "
                 f"`artifact` flag is set. Maintenance window [-3, 0] s is identical for "
                 f"every trial, so each included trial = one maintenance epoch.")
    lines.append(f"- Target: `load_binary` (0 = set size 4 / low; 1 = set sizes 6,8 / high).")
    lines.append("")
    lines.append("## Per-subject trial counts")
    lines.append("")
    lines.append("| Subject | Sessions | Total | Artifact | Incl. | Low (ss4) | High (ss6/8) | Ratio | Triggers |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for _, r in audit.iterrows():
        lines.append(f"| {r['subject_id']} | {r['n_sessions']} | {r['n_trials_total']} | "
                     f"{r['n_artifact']} ({r['artifact_frac']*100:.1f}%) | {r['n_included']} | "
                     f"{r['n_low_ss4']} | {r['n_high_ss68']} | {r['high_low_ratio']} | "
                     f"{r['triggers'] or '-'} |")
    lines.append("")
    lines.append(f"**Subjects with at least one discussion trigger: {n_with_triggers} / {len(audit)}**")
    lines.append("")
    lines.append("Trigger legend (from the controls spec): `empty_class` = a binary class has 0 trials; "
                 f"`thin_class` = <{MIN_PER_CLASS} in a class; `imbalance` = high/low ratio > {MAX_CLASS_RATIO:.0f}:1; "
                 f"`exclusions` = >{int(MAX_EXCLUSION_FRAC*100)}% trials artifact-flagged.")
    lines.append("")
    lines.append("## Counts by set size (included trials)")
    lines.append("")
    lines.append("| Subject | " + " | ".join(f"ss{c}" for c in by_ss.columns) + " |")
    lines.append("|---|" + "|".join("---" for _ in by_ss.columns) + "|")
    for sub, r in by_ss.iterrows():
        lines.append(f"| {sub} | " + " | ".join(str(int(v)) for v in r.values) + " |")
    lines.append("")
    lines.append("## Scalp montage across subjects (load-bearing for LOSO)")
    lines.append("")
    lines.append("The scalp montage is **not uniform** across subjects. LOSO features must "
                 "live in the channel space shared by every held-out subject.")
    lines.append("")
    lines.append(f"- **Common intersection ({montage_out['n_common']} channels):** "
                 f"`{', '.join(common_sorted)}`")
    lines.append(f"- **Excluding ear/mastoid references A1/A2 "
                 f"({montage_out['n_common_brain_excl_refs']} brain channels):** "
                 f"`{', '.join(brain_common)}`")
    lines.append("")
    lines.append("| Subject | #channels | channels |")
    lines.append("|---|---|---|")
    for s, chans in montage_out["per_subject_channels"].items():
        lines.append(f"| {s} | {len(chans)} | {', '.join(chans)} |")
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    if n_with_triggers == 0:
        lines.append("- No trial-count trigger fired: the predeclared **+0.075** balanced-accuracy "
                     "bar stands on the count side, pending agreement on the montage constraint below.")
    else:
        lines.append(f"- {n_with_triggers} subject(s) fired a count trigger; Claude and Codex should "
                     "review whether +0.075 remains fair before any decoder is fit.")
    lines.append(f"- The common LOSO montage is only **{montage_out['n_common_brain_excl_refs']} brain "
                 "channels** -- a real spatial-resolution constraint not known when +0.075 was set. "
                 "Flagged for Claude-Codex discussion before modeling.")

    md_path = os.path.join(args.out_dir, "trial_count_audit.md")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    # ---- Console summary ----
    print("\n" + "\n".join(lines[:4]))
    print(f"\nPer-subject audit:\n{audit.to_string(index=False)}")
    print(f"\nCommon montage intersection ({len(common_sorted)} ch, "
          f"{len(brain_common)} brain): {common_sorted}")
    print(f"\nWrote:\n  {audit_csv}\n  "
          f"{os.path.join(args.out_dir, 'trial_count_by_setsize.csv')}\n  "
          f"{os.path.join(args.out_dir, 'montage_intersection.json')}\n  {md_path}")
    print(f"\nSubjects with triggers: {n_with_triggers}/{len(audit)}")


if __name__ == "__main__":
    main()
