"""Evaluate the prospective Part B MTL coupling confirmatory gate.

The gate operationalizes Amendment 1's stricter requirement for the mechanism lead:
the fixed EEGNet score-to-MTL theta-alpha relationship must survive task-schedule
residualization and subject-level robustness. This script consumes the residual coupling
outputs from ``run_mtl_residual_coupling_probe.py`` and writes a compact pass/fail
record. It does not fit a new model and it does not reinterpret raw coupling as
confirmatory evidence.

Default gate:
    - fixed metric: schedule-residualized EEGNet score vs MTL theta-alpha differential
    - mean correlation > 0
    - at least 7 of 9 subjects positive
    - exact two-sided subject sign-flip p <= 0.05
    - no leave-one-subject-out mean <= 0

Usage:
    .\\venv\\Scripts\\python.exe scripts\\run_mtl_confirmatory_coupling_gate.py \\
        --residual-summary outputs\\mechanism\\mtl_residual_coupling_summary_eegnet_raw_all.json \\
        --subject-summary outputs\\mechanism\\mtl_residual_coupling_subject_summary_eegnet_raw_all.csv \\
        --out-dir outputs\\mechanism
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


CONFIRMATORY_METRIC = "corr_schedule_residual_score_mtl_theta_alpha_diff"


def _load_json(path: str) -> dict[str, Any]:
    """Load and validate a JSON object."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}.")
    return data


def _derive_tag(summary: dict[str, Any], path: str) -> str:
    """Derive an output tag from the summary object or filename."""
    if summary.get("tag"):
        return str(summary["tag"])
    stem = Path(path).stem
    prefix = "mtl_residual_coupling_summary_"
    return stem[len(prefix):] if stem.startswith(prefix) else stem


def _require_metric(summary: dict[str, Any], metric: str) -> dict[str, Any]:
    """Return ``metric`` from ``summary['metric_summary']`` with clear errors."""
    metrics = summary.get("metric_summary")
    if not isinstance(metrics, dict):
        raise ValueError("Residual summary missing metric_summary object.")
    item = metrics.get(metric)
    if not isinstance(item, dict):
        raise ValueError(f"Residual summary missing metric {metric!r}.")
    required = {"n_subjects", "mean", "n_positive", "sign_flip_p_two_sided"}
    missing = sorted(required - set(item))
    if missing:
        raise ValueError(f"Metric {metric!r} missing keys: {missing}")
    return item


def _leave_one_out_min(values: np.ndarray) -> float:
    """Return the smallest leave-one-subject-out mean."""
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    if len(finite) <= 1:
        return float("nan")
    return float(min(np.mean(np.delete(finite, idx)) for idx in range(len(finite))))


def _gate_result(
    metric: dict[str, Any],
    subject_df: pd.DataFrame,
    metric_column: str,
    alpha: float,
    min_positive_subjects: int,
    min_loo_mean: float,
) -> dict[str, Any]:
    """Evaluate the confirmatory gate and return observed values plus decisions."""
    if metric_column not in subject_df.columns:
        raise ValueError(f"Subject summary missing metric column {metric_column!r}.")
    values = subject_df[metric_column].to_numpy(dtype=float)
    loo_min = _leave_one_out_min(values)
    observed = {
        "n_subjects": int(metric["n_subjects"]),
        "mean": float(metric["mean"]),
        "n_positive": int(metric["n_positive"]),
        "sign_flip_p_two_sided": float(metric["sign_flip_p_two_sided"]),
        "min_leave_one_subject_out_mean": loo_min,
    }
    criteria = {
        "mean_positive": observed["mean"] > 0.0,
        "positive_subjects": observed["n_positive"] >= min_positive_subjects,
        "sign_flip_p": observed["sign_flip_p_two_sided"] <= alpha,
        "leave_one_subject_out": loo_min > min_loo_mean,
    }
    return {
        "observed": observed,
        "criteria": {
            "metric": metric_column,
            "alpha": alpha,
            "min_positive_subjects": min_positive_subjects,
            "min_leave_one_subject_out_mean_exclusive": min_loo_mean,
            "required_mean_direction": "positive",
        },
        "criteria_met": criteria,
        "gate_passed": bool(all(criteria.values())),
    }


def _json_default(value: Any) -> Any:
    """Convert NumPy and non-finite values for JSON serialization."""
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        value = float(value)
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def _fmt(value: Any, digits: int = 3) -> str:
    """Format a numeric value for Markdown."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not np.isfinite(value):
        return "NA"
    return f"{value:.{digits}f}"


def _write_markdown(path: str, packet: dict[str, Any], subject_df: pd.DataFrame) -> None:
    """Write the confirmatory gate report."""
    result = packet["confirmatory_gate"]
    observed = result["observed"]
    criteria = result["criteria"]
    checks = result["criteria_met"]
    status = "PASS" if result["gate_passed"] else "FAIL"

    lines = [
        f"# MTL Confirmatory Coupling Gate - {packet['tag']}",
        "",
        f"**Gate result:** {status}",
        "",
        "This is the prospective Amendment 1 mechanism gate. It fixes the metric to the",
        "schedule-residualized EEGNet score vs MTL theta-alpha differential and requires",
        "the effect to survive subject-level robustness checks. Raw coupling is reported",
        "only as context, not as the pass criterion.",
        "",
        "## Fixed Criterion",
        "",
        f"- Metric: `{criteria['metric']}`",
        f"- Mean direction: {criteria['required_mean_direction']}",
        f"- Positive subjects required: >= {criteria['min_positive_subjects']}",
        f"- Two-sided subject sign-flip p required: <= {_fmt(criteria['alpha'], 4)}",
        f"- Minimum leave-one-subject-out mean required: > {_fmt(criteria['min_leave_one_subject_out_mean_exclusive'])}",
        "",
        "## Observed",
        "",
        "| Quantity | Observed | Pass? |",
        "| --- | ---: | ---: |",
        f"| Mean correlation | {_fmt(observed['mean'])} | {'yes' if checks['mean_positive'] else 'no'} |",
        f"| Positive subjects | {observed['n_positive']}/{observed['n_subjects']} | {'yes' if checks['positive_subjects'] else 'no'} |",
        f"| Two-sided sign-flip p | {_fmt(observed['sign_flip_p_two_sided'], 4)} | {'yes' if checks['sign_flip_p'] else 'no'} |",
        f"| Min leave-one-subject-out mean | {_fmt(observed['min_leave_one_subject_out_mean'])} | {'yes' if checks['leave_one_subject_out'] else 'no'} |",
        "",
        "## Interpretation",
        "",
        packet["interpretation"],
        "",
        "## Subject Values",
        "",
        "| Subject | Schedule-residual corr |",
        "| --- | ---: |",
    ]
    for row in subject_df[["subject_id", CONFIRMATORY_METRIC]].itertuples(index=False):
        lines.append(f"| {row.subject_id} | {_fmt(getattr(row, CONFIRMATORY_METRIC))} |")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    """CLI entrypoint."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--residual-summary", required=True, help="Residual coupling JSON summary.")
    ap.add_argument("--subject-summary", required=True, help="Residual coupling subject CSV.")
    ap.add_argument("--out-dir", default="outputs/mechanism", help="Output directory.")
    ap.add_argument("--tag", default=None, help="Optional output tag.")
    ap.add_argument("--alpha", type=float, default=0.05, help="Two-sided sign-flip alpha.")
    ap.add_argument("--min-positive-subjects", type=int, default=7, help="Required positive subjects.")
    ap.add_argument(
        "--min-loo-mean",
        type=float,
        default=0.0,
        help="Exclusive lower bound for every leave-one-subject-out mean.",
    )
    args = ap.parse_args()

    summary = _load_json(args.residual_summary)
    subject_df = pd.read_csv(args.subject_summary)
    metric = _require_metric(summary, CONFIRMATORY_METRIC)
    tag = args.tag or _derive_tag(summary, args.residual_summary)
    gate = _gate_result(
        metric=metric,
        subject_df=subject_df,
        metric_column=CONFIRMATORY_METRIC,
        alpha=args.alpha,
        min_positive_subjects=args.min_positive_subjects,
        min_loo_mean=args.min_loo_mean,
    )
    packet = {
        "tag": tag,
        "inputs": {
            "residual_summary": args.residual_summary,
            "subject_summary": args.subject_summary,
        },
        "confirmatory_gate": gate,
        "context_metrics": {
            "raw": _require_metric(summary, "corr_raw_score_mtl_theta_alpha_diff"),
            "load_residualized": _require_metric(summary, "corr_load_residual_score_mtl_theta_alpha_diff"),
            "schedule_residualized": metric,
            "behavior_residualized": _require_metric(summary, "corr_behavior_residual_score_mtl_theta_alpha_diff"),
        },
        "interpretation": (
            "The Part B confirmatory gate is not met. The fixed schedule-residualized "
            "coupling is near zero, has only 4/9 positive subjects, and has a two-sided "
            "subject sign-flip p-value far above 0.05. Part B remains an exploratory "
            "mechanism lead rather than validated deep-source readout."
        ),
    }

    os.makedirs(args.out_dir, exist_ok=True)
    json_path = Path(args.out_dir) / f"mtl_confirmatory_coupling_gate_{tag}.json"
    md_path = Path(args.out_dir) / f"mtl_confirmatory_coupling_gate_{tag}.md"
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(packet, fh, indent=2, default=_json_default, allow_nan=False)
    _write_markdown(str(md_path), packet, subject_df)

    result = packet["confirmatory_gate"]
    observed = result["observed"]
    print(f"MTL confirmatory coupling gate: {tag}")
    print(f"  gate_passed={result['gate_passed']}")
    print(
        "  schedule_residualized: "
        f"mean={observed['mean']:.3f}, "
        f"positive={observed['n_positive']}/{observed['n_subjects']}, "
        f"p2={observed['sign_flip_p_two_sided']:.4f}, "
        f"min_loo_mean={observed['min_leave_one_subject_out_mean']:.3f}"
    )
    print(f"\nWrote:\n  {json_path}\n  {md_path}")


if __name__ == "__main__":
    main()
