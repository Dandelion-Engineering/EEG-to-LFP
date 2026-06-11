"""Summarize subject-level signal-vs-control statistics for the load decoder.

The Claim Sheet's headline bar is evaluated at the held-out-subject level:

* mean(signal balanced accuracy - strongest non-signal control) >= 0.075;
* at least 7 of 9 held-out subjects above the strongest control;
* no single-subject removal drops the mean improvement below 0.04.

This script computes those quantities from ``run_control_models.py`` output and writes
both machine-readable and human-readable summaries.

Usage:
    .\\venv\\Scripts\\python.exe scripts\\summarize_subject_statistics.py \\
        --control-subject-scores outputs\\controls\\control_subject_scores_logistic_all_all.csv \\
        --out-dir outputs\\statistics
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

CONTROL_COLUMNS = {
    "behavioral": "behavioral_ba",
    "timing": "timing_ba",
    "label_shuffle": "label_shuffle_ba_mean",
}


def _derive_tag(path: str) -> str:
    """Derive the run tag from a control_subject_scores_<tag>.csv filename."""
    name = Path(path).stem
    prefix = "control_subject_scores_"
    return name[len(prefix):] if name.startswith(prefix) else name


def _sign_flip_distribution(improvements: np.ndarray) -> np.ndarray:
    """Return the exact subject-level sign-flip null distribution of the mean."""
    magnitudes = np.abs(improvements)
    vals = []
    for signs in itertools.product((-1.0, 1.0), repeat=len(magnitudes)):
        vals.append(float(np.mean(magnitudes * np.asarray(signs))))
    return np.asarray(vals, dtype=np.float64)


def _bootstrap_mean_ci(improvements: np.ndarray, seed: int, n_bootstrap: int) -> tuple[float, float]:
    """Return a subject-bootstrap percentile interval for mean improvement."""
    rng = np.random.default_rng(seed)
    n = len(improvements)
    draws = rng.choice(improvements, size=(n_bootstrap, n), replace=True).mean(axis=1)
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--control-subject-scores", required=True, help="control_subject_scores_<tag>.csv.")
    ap.add_argument("--out-dir", default="outputs/statistics", help="Output directory.")
    ap.add_argument("--tag", default=None, help="Optional output tag.")
    ap.add_argument("--success-margin", type=float, default=0.075)
    ap.add_argument("--min-positive-subjects", type=int, default=7)
    ap.add_argument("--min-leave-one-out-mean", type=float, default=0.04)
    ap.add_argument("--bootstrap-samples", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    tag = args.tag or _derive_tag(args.control_subject_scores)
    scores = pd.read_csv(args.control_subject_scores).sort_values("subject_id").reset_index(drop=True)
    required = {"subject_id", "signal_ba"} | set(CONTROL_COLUMNS.values())
    missing = sorted(required - set(scores.columns))
    if missing:
        raise ValueError(f"Missing required score columns: {missing}")

    control_matrix = scores[list(CONTROL_COLUMNS.values())].to_numpy(dtype=np.float64)
    strongest_idx = np.argmax(control_matrix, axis=1)
    strongest_names = np.array(list(CONTROL_COLUMNS.keys()))[strongest_idx]
    strongest_values = control_matrix[np.arange(len(scores)), strongest_idx]
    improvements = scores["signal_ba"].to_numpy(dtype=np.float64) - strongest_values

    scores["strongest_control"] = strongest_names
    scores["strongest_control_ba"] = strongest_values
    scores["improvement"] = improvements
    scores["above_strongest_control"] = improvements > 0.0
    scores["decoding_verdict"] = np.where(improvements > 0.0, "beats_control", "does_not_beat_control")

    mean_improvement = float(np.mean(improvements))
    n_positive = int(np.sum(improvements > 0.0))
    leave_one_out = []
    for i, subject in enumerate(scores["subject_id"].tolist()):
        value = float(np.mean(np.delete(improvements, i)))
        leave_one_out.append({"removed_subject": subject, "mean_improvement": value})
    min_loo = float(min(row["mean_improvement"] for row in leave_one_out))

    sign_flip = _sign_flip_distribution(improvements)
    observed = mean_improvement
    sign_flip_p_one_sided = float(np.mean(sign_flip >= observed))
    sign_flip_p_two_sided = float(np.mean(np.abs(sign_flip) >= abs(observed)))
    sign_flip_null_interval = [float(np.quantile(sign_flip, 0.025)), float(np.quantile(sign_flip, 0.975))]
    bootstrap_ci = _bootstrap_mean_ci(improvements, args.seed, args.bootstrap_samples)

    headline_success = (
        mean_improvement >= args.success_margin
        and n_positive >= args.min_positive_subjects
        and min_loo >= args.min_leave_one_out_mean
    )

    summary = {
        "tag": tag,
        "n_subjects": int(len(scores)),
        "mean_signal_ba": float(scores["signal_ba"].mean()),
        "mean_strongest_control_ba": float(scores["strongest_control_ba"].mean()),
        "mean_improvement": mean_improvement,
        "subjects_above_strongest_control": n_positive,
        "min_leave_one_out_mean_improvement": min_loo,
        "headline_success": bool(headline_success),
        "success_criteria": {
            "mean_improvement_at_least": args.success_margin,
            "positive_subjects_at_least": args.min_positive_subjects,
            "leave_one_out_mean_at_least": args.min_leave_one_out_mean,
        },
        "subject_level_sign_flip": {
            "p_one_sided_mean_at_least_observed": sign_flip_p_one_sided,
            "p_two_sided_abs_mean_at_least_observed": sign_flip_p_two_sided,
            "null_interval_2p5_97p5": sign_flip_null_interval,
        },
        "subject_bootstrap_mean_ci_2p5_97p5": [bootstrap_ci[0], bootstrap_ci[1]],
        "leave_one_out": leave_one_out,
    }

    subject_path = os.path.join(args.out_dir, f"subject_statistics_{tag}.csv")
    json_path = os.path.join(args.out_dir, f"summary_{tag}.json")
    md_path = os.path.join(args.out_dir, f"summary_{tag}.md")
    scores.to_csv(subject_path, index=False)
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    lines = [
        f"# Subject Statistics - {tag}",
        "",
        f"- Mean signal balanced accuracy: {summary['mean_signal_ba']:.3f}",
        f"- Mean strongest-control balanced accuracy: {summary['mean_strongest_control_ba']:.3f}",
        f"- Mean improvement: {mean_improvement:.3f}",
        f"- Subjects above strongest control: {n_positive}/{len(scores)}",
        f"- Minimum leave-one-subject-removed mean improvement: {min_loo:.3f}",
        f"- Headline success criteria met: {'yes' if headline_success else 'no'}",
        f"- Subject sign-flip p(one-sided >= observed): {sign_flip_p_one_sided:.4f}",
        f"- Subject bootstrap 95% CI for mean improvement: [{bootstrap_ci[0]:.3f}, {bootstrap_ci[1]:.3f}]",
        "",
        "| Subject | Signal BA | Strongest control | Control BA | Improvement |",
        "| --- | ---: | --- | ---: | ---: |",
    ]
    for row in scores.itertuples(index=False):
        lines.append(
            f"| {row.subject_id} | {row.signal_ba:.3f} | {row.strongest_control} | "
            f"{row.strongest_control_ba:.3f} | {row.improvement:.3f} |"
        )
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"Statistics run: {tag}")
    print(f"  mean improvement: {mean_improvement:.3f}")
    print(f"  subjects above strongest control: {n_positive}/{len(scores)}")
    print(f"  min leave-one-out mean: {min_loo:.3f}")
    print(f"  headline success criteria met: {'yes' if headline_success else 'no'}")
    print(f"Wrote:\n  {subject_path}\n  {json_path}\n  {md_path}")


if __name__ == "__main__":
    main()
