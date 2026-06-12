"""Export report-ready figures from the verification dashboard inputs.

This script consumes the same final EEGNet summary/statistics/mechanism files used by
``render_verification_dashboard.py`` and writes 300-DPI-or-higher PNGs for the
Technical Report. It does not recompute any model result.

Usage:
    .\\venv\\Scripts\\python.exe scripts\\export_dashboard_report_figures.py \\
        --subject-statistics outputs\\statistics\\subject_statistics_eegnet_raw_all.csv \\
        --summary outputs\\statistics\\summary_eegnet_raw_all.json \\
        --mechanism-gate outputs\\mechanism\\mtl_confirmatory_coupling_gate_eegnet_raw_all.json \\
        --mechanism-subject-summary outputs\\mechanism\\mtl_residual_coupling_subject_summary_eegnet_raw_all.csv \\
        --out-dir deliverables\\technical_report\\figures
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


COUPLING_COLUMNS = [
    ("raw", "corr_raw_score_mtl_theta_alpha_diff", "Raw"),
    ("load_residualized", "corr_load_residual_score_mtl_theta_alpha_diff", "Load residualized"),
    ("schedule_residualized", "corr_schedule_residual_score_mtl_theta_alpha_diff", "Schedule residualized"),
    ("behavior_residualized", "corr_behavior_residual_score_mtl_theta_alpha_diff", "Behavior residualized"),
]


def _load_json(path: str) -> dict:
    """Load and validate a JSON object."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}.")
    return data


def _require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    """Raise a useful error when a table is missing expected columns."""
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{label} missing required columns: {missing}")


def _save(fig: plt.Figure, out_path: Path, dpi: int) -> None:
    """Save a Matplotlib figure with consistent report settings."""
    fig.tight_layout()
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out_path} at {dpi} DPI")


def plot_subject_improvements(stats: pd.DataFrame, summary: dict, out_path: Path, dpi: int) -> None:
    """Plot per-subject EEGNet improvement over the strongest control."""
    stats = stats.sort_values("subject_id").reset_index(drop=True)
    subjects = stats["subject_id"].tolist()
    improvements = stats["improvement"].astype(float).to_numpy()
    colors = ["#2f7d5b" if value > 0 else "#a94442" for value in improvements]

    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    bars = ax.bar(subjects, improvements, color=colors, edgecolor="#20252b", linewidth=0.7)
    ax.axhline(0.0, color="#20252b", linewidth=1.0)
    ax.axhline(
        float(summary["success_criteria"]["mean_improvement_at_least"]),
        color="#7a5c00",
        linestyle="--",
        linewidth=1.1,
        label="Pre-declared mean bar (+0.075)",
    )
    ax.axhline(
        float(summary["mean_improvement"]),
        color="#2454a6",
        linestyle="-.",
        linewidth=1.1,
        label=f"Observed mean ({summary['mean_improvement']:+.3f})",
    )

    for bar, value in zip(bars, improvements, strict=True):
        va = "bottom" if value >= 0 else "top"
        offset = 0.006 if value >= 0 else -0.006
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + offset,
            f"{value:+.3f}",
            ha="center",
            va=va,
            fontsize=8,
        )

    summary_text = (
        f"Signal BA: {summary['mean_signal_ba']:.3f}\n"
        f"Control BA: {summary['mean_strongest_control_ba']:.3f}\n"
        f"Above control: {summary['subjects_above_strongest_control']}/{summary['n_subjects']}\n"
        f"Min LOO mean: {summary['min_leave_one_out_mean_improvement']:+.3f}\n"
        "Headline: not met"
    )
    ax.text(
        0.99,
        0.04,
        summary_text,
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "#f6f7f9", "edgecolor": "#cfd6df"},
    )
    ax.set_title("EEGNet LOSO improvement over strongest non-signal control")
    ax.set_ylabel("Balanced-accuracy improvement")
    ax.set_xlabel("Held-out subject")
    ax.set_ylim(min(-0.09, improvements.min() - 0.035), max(0.245, improvements.max() + 0.035))
    ax.grid(axis="y", color="#d8dee6", linewidth=0.8, alpha=0.8)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", fontsize=8, frameon=False)
    _save(fig, out_path, dpi)


def plot_coupling_residualization(subjects: pd.DataFrame, gate: dict, out_path: Path, dpi: int) -> None:
    """Plot the raw and residualized EEGNet-to-MTL coupling metrics."""
    required = {"subject_id"} | {column for _, column, _ in COUPLING_COLUMNS}
    _require_columns(subjects, required, "Mechanism subject summary")

    context = gate["context_metrics"]
    labels = [label for _, _, label in COUPLING_COLUMNS]
    means = [float(context[key]["mean"]) for key, _, _ in COUPLING_COLUMNS]
    pvals = [float(context[key]["sign_flip_p_two_sided"]) for key, _, _ in COUPLING_COLUMNS]
    positive = [int(context[key]["n_positive"]) for key, _, _ in COUPLING_COLUMNS]
    n_subjects = int(context[COUPLING_COLUMNS[0][0]]["n_subjects"])
    x = list(range(len(COUPLING_COLUMNS)))
    palette = ["#5c7ea8", "#7b8b4d", "#b25d4a", "#8467a9"]

    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    ax.bar(x, means, color=palette, edgecolor="#20252b", linewidth=0.7, width=0.62)
    for idx, (_, column, _) in enumerate(COUPLING_COLUMNS):
        values = subjects[column].astype(float).to_numpy()
        jitter = [idx + (offset - (len(values) - 1) / 2) * 0.018 for offset in range(len(values))]
        ax.scatter(jitter, values, s=24, color="#20252b", alpha=0.78, zorder=3)
        ax.text(
            idx,
            max(means[idx], 0.0) + 0.025,
            f"{positive[idx]}/{n_subjects}+\np={pvals[idx]:.3f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    observed_gate = gate["confirmatory_gate"]["observed"]
    gate_text = (
        "Confirmatory gate: not met\n"
        f"fixed metric mean={observed_gate['mean']:+.3f}, "
        f"{observed_gate['n_positive']}/{observed_gate['n_subjects']} positive, "
        f"p={observed_gate['sign_flip_p_two_sided']:.3f}"
    )
    ax.text(
        0.02,
        0.04,
        gate_text,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "#f6f7f9", "edgecolor": "#cfd6df"},
    )
    ax.axhline(0.0, color="#20252b", linewidth=1.0)
    ax.set_xticks(x, labels, rotation=12, ha="right")
    ax.set_ylabel("Subject-level corr(score, MTL theta-alpha)")
    ax.set_title("EEGNet-to-MTL coupling weakens after task-structure residualization")
    ax.set_ylim(-0.145, 0.315)
    ax.grid(axis="y", color="#d8dee6", linewidth=0.8, alpha=0.8)
    ax.set_axisbelow(True)
    _save(fig, out_path, dpi)


def main() -> None:
    """Parse arguments and write all report figures."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--subject-statistics", required=True, help="subject_statistics_<tag>.csv.")
    ap.add_argument("--summary", required=True, help="summary_<tag>.json.")
    ap.add_argument("--mechanism-gate", required=True, help="MTL confirmatory gate JSON.")
    ap.add_argument("--mechanism-subject-summary", required=True, help="Residual-coupling subject CSV.")
    ap.add_argument("--out-dir", default="deliverables/technical_report/figures", help="Output directory.")
    ap.add_argument("--tag", default="eegnet_raw_all", help="Output filename tag.")
    ap.add_argument("--dpi", type=int, default=300, help="PNG export DPI; must be at least 300.")
    args = ap.parse_args()

    if args.dpi < 300:
        raise ValueError("--dpi must be at least 300 for Technical Report figures.")

    stats = pd.read_csv(args.subject_statistics)
    _require_columns(
        stats,
        {
            "subject_id",
            "signal_ba",
            "strongest_control_ba",
            "improvement",
            "above_strongest_control",
        },
        "Subject statistics",
    )
    summary = _load_json(args.summary)
    gate = _load_json(args.mechanism_gate)
    mechanism_subjects = pd.read_csv(args.mechanism_subject_summary)

    out_dir = Path(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    plot_subject_improvements(stats, summary, out_dir / f"{args.tag}_subject_improvements.png", args.dpi)
    plot_coupling_residualization(
        mechanism_subjects,
        gate,
        out_dir / f"{args.tag}_mtl_coupling_residualization.png",
        args.dpi,
    )


if __name__ == "__main__":
    main()
