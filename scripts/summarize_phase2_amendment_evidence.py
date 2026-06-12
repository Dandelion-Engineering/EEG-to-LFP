"""Compile fixed Phase 2 evidence for a Claim Sheet amendment discussion.

This script does not run new analyses and does not declare project success.
It reads already-generated decoding, behavioral-control, and mechanism summaries
and writes a compact evidence packet for the post-EEGNet amendment discussion.

Example:
    .\\venv\\Scripts\\python.exe scripts\\summarize_phase2_amendment_evidence.py \\
        --statistics-summary outputs\\statistics\\summary_eegnet_raw_all.json \\
        --behavioral-ablation-summary outputs\\controls\\behavioral_ablation_summary.json \\
        --bandpower-summary outputs\\mechanism\\mtl_bandpower_summary_eegnet_raw_all.json \\
        --residual-summary outputs\\mechanism\\mtl_residual_coupling_summary_eegnet_raw_all.json \\
        --out-dir outputs\\amendment
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


def _load_json(path: str) -> dict[str, Any]:
    """Load a JSON object from ``path``."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}.")
    return data


def _require_keys(data: dict[str, Any], required: set[str], label: str) -> None:
    """Raise a clear error if ``data`` lacks required keys."""
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"{label} missing required keys: {missing}")


def _metric(summary: dict[str, Any], metric: str) -> dict[str, Any]:
    """Return a named metric entry from a summary's ``metric_summary``."""
    metrics = summary.get("metric_summary")
    if not isinstance(metrics, dict) or metric not in metrics:
        raise ValueError(f"Metric {metric!r} not found in metric_summary.")
    value = metrics[metric]
    if not isinstance(value, dict):
        raise ValueError(f"Metric {metric!r} must be a JSON object.")
    return value


def _best_behavioral_component(ablation: dict[str, Any]) -> dict[str, Any]:
    """Return the highest-mean behavioral ablation component."""
    components = ablation.get("components")
    if not isinstance(components, list) or not components:
        raise ValueError("Behavioral ablation summary has no components.")
    return max(components, key=lambda item: float(item["mean_ba"]))


def _target_rate(rows: list[dict[str, Any]], value: str) -> dict[str, Any]:
    """Find a previous-trial target-rate row by its string-coded value."""
    for row in rows:
        if str(row.get("previous_trial_correct")) == value:
            return row
    raise ValueError(f"Missing previous_trial_correct={value!r} rate row.")


def _json_default(value: Any) -> Any:
    """Convert non-finite floats to JSON null."""
    if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
        return None
    return value


def _compile_packet(
    statistics: dict[str, Any],
    ablation: dict[str, Any],
    bandpower: dict[str, Any],
    residual: dict[str, Any],
    inputs: dict[str, str],
) -> dict[str, Any]:
    """Assemble a compact amendment evidence packet."""
    _require_keys(
        statistics,
        {
            "tag",
            "n_subjects",
            "mean_signal_ba",
            "mean_strongest_control_ba",
            "mean_improvement",
            "subjects_above_strongest_control",
            "min_leave_one_out_mean_improvement",
            "headline_success",
            "success_criteria",
            "subject_bootstrap_mean_ci_2p5_97p5",
        },
        "Statistics summary",
    )
    _require_keys(
        ablation,
        {"n_subjects", "components", "previous_trial_correct_target_rates"},
        "Behavioral ablation summary",
    )
    _require_keys(bandpower, {"tag", "n_trials", "n_subjects", "metric_summary"}, "Bandpower summary")
    _require_keys(residual, {"tag", "n_trials", "n_subjects", "metric_summary"}, "Residual summary")

    criteria = statistics["success_criteria"]
    best_component = _best_behavioral_component(ablation)
    previous_zero = _target_rate(ablation["previous_trial_correct_target_rates"], "0.0")
    previous_one = _target_rate(ablation["previous_trial_correct_target_rates"], "1.0")
    previous_missing = _target_rate(ablation["previous_trial_correct_target_rates"], "missing")

    mtl_substrate = _metric(bandpower, "mtl_theta_alpha_log_power_diff_load_effect_z")
    raw_coupling = _metric(residual, "corr_raw_score_mtl_theta_alpha_diff")
    load_residual = _metric(residual, "corr_load_residual_score_mtl_theta_alpha_diff")
    schedule_residual = _metric(residual, "corr_schedule_residual_score_mtl_theta_alpha_diff")
    behavior_residual = _metric(residual, "corr_behavior_residual_score_mtl_theta_alpha_diff")

    return {
        "tag": statistics["tag"],
        "inputs": inputs,
        "decoding_boundary": {
            "headline_success": bool(statistics["headline_success"]),
            "mean_signal_ba": statistics["mean_signal_ba"],
            "mean_strongest_control_ba": statistics["mean_strongest_control_ba"],
            "mean_improvement": statistics["mean_improvement"],
            "required_mean_improvement": criteria["mean_improvement_at_least"],
            "subjects_above_strongest_control": statistics["subjects_above_strongest_control"],
            "required_positive_subjects": criteria["positive_subjects_at_least"],
            "min_leave_one_out_mean_improvement": statistics["min_leave_one_out_mean_improvement"],
            "required_leave_one_out_mean": criteria["leave_one_out_mean_at_least"],
            "bootstrap_ci_95": statistics["subject_bootstrap_mean_ci_2p5_97p5"],
        },
        "behavioral_control": {
            "best_component": best_component,
            "previous_trial_correct_target_rates": {
                "previous_incorrect": previous_zero,
                "previous_correct": previous_one,
                "missing": previous_missing,
            },
            "interpretation": (
                "The strongest non-signal control is explained by previous-trial correctness, "
                "matching the task rule that an incorrect response is followed by a set-size-4 trial."
            ),
        },
        "mechanism_evidence": {
            "mtl_theta_alpha_load_substrate": mtl_substrate,
            "raw_score_to_mtl_coupling": raw_coupling,
            "load_residualized_coupling": load_residual,
            "schedule_residualized_coupling": schedule_residual,
            "behavior_residualized_coupling": behavior_residual,
        },
        "amendment_guard": {
            "part_a": (
                "Treat the completed common-montage LOSO model ladder as a clean negative "
                "boundary under the original decoding bar."
            ),
            "part_b": (
                "Treat the EEGNet score to MTL theta-alpha relationship as an exploratory "
                "mechanism lead. Do not call it validated deep-source readout unless a "
                "separately agreed confirmatory/robustness bar is met."
            ),
            "do_not_do": [
                "Do not add another headline decoder to rescue the original bar after seeing results.",
                "Do not convert the raw p~=0.0508 coupling into confirmatory evidence post hoc.",
                "Do not omit the residualized sensitivity rows from amendment language.",
            ],
        },
    }


def _fmt_float(value: Any, digits: int = 3) -> str:
    """Format a float-like value for Markdown."""
    if value is None:
        return "NA"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{number:.{digits}f}"


def _fmt_p(value: Any) -> str:
    """Format a p-value for Markdown."""
    return _fmt_float(value, 4)


def _write_markdown(path: str, packet: dict[str, Any]) -> None:
    """Write the amendment evidence packet as Markdown."""
    decoding = packet["decoding_boundary"]
    behavioral = packet["behavioral_control"]
    mechanism = packet["mechanism_evidence"]
    guard = packet["amendment_guard"]

    best = behavioral["best_component"]
    prev = behavioral["previous_trial_correct_target_rates"]

    lines = [
        f"# Phase 2 Amendment Evidence - {packet['tag']}",
        "",
        "> Evidence packet only. This file compiles completed Phase 2 summaries for the",
        "> amendment discussion; it does not modify the Claim Sheet or declare success.",
        "",
        "## Decoding Boundary",
        "",
        "| Quantity | Observed | Required |",
        "| --- | ---: | ---: |",
        f"| Mean signal balanced accuracy | {_fmt_float(decoding['mean_signal_ba'])} | - |",
        f"| Mean strongest-control balanced accuracy | {_fmt_float(decoding['mean_strongest_control_ba'])} | - |",
        f"| Mean improvement | {_fmt_float(decoding['mean_improvement'])} | >= {_fmt_float(decoding['required_mean_improvement'])} |",
        f"| Subjects above strongest control | {decoding['subjects_above_strongest_control']}/9 | >= {decoding['required_positive_subjects']}/9 |",
        f"| Min leave-one-subject-removed mean | {_fmt_float(decoding['min_leave_one_out_mean_improvement'])} | >= {_fmt_float(decoding['required_leave_one_out_mean'])} |",
        f"| Bootstrap 95% CI | [{_fmt_float(decoding['bootstrap_ci_95'][0])}, {_fmt_float(decoding['bootstrap_ci_95'][1])}] | excludes 0 |",
        f"| Headline success | {'yes' if decoding['headline_success'] else 'no'} | yes |",
        "",
        "Interpretation: the locked common-montage LOSO decoding bar is not met,",
        "and the positive EEGNet mean is not robust enough to rescue the original claim.",
        "",
        "## Behavioral Control Source",
        "",
        f"- Strongest ablation component: `{best['component']}` ({best['description']}), mean BA {_fmt_float(best['mean_ba'])}.",
        f"- Previous incorrect -> current high-load rate: {_fmt_float(prev['previous_incorrect']['high_load_rate'])} ({prev['previous_incorrect']['n_trials']} trials).",
        f"- Previous correct -> current high-load rate: {_fmt_float(prev['previous_correct']['high_load_rate'])} ({prev['previous_correct']['n_trials']} trials).",
        f"- Missing previous-trial value -> current high-load rate: {_fmt_float(prev['missing']['high_load_rate'])} ({prev['missing']['n_trials']} trials).",
        "",
        behavioral["interpretation"],
        "",
        "## Mechanism Evidence",
        "",
        "| Metric | Mean | Positive subjects | Two-sided sign-flip p |",
        "| --- | ---: | ---: | ---: |",
    ]

    mechanism_rows = [
        ("MTL theta-alpha load substrate", mechanism["mtl_theta_alpha_load_substrate"]),
        ("Raw EEGNet score vs MTL theta-alpha", mechanism["raw_score_to_mtl_coupling"]),
        ("Load-residualized coupling", mechanism["load_residualized_coupling"]),
        ("Schedule-residualized coupling", mechanism["schedule_residualized_coupling"]),
        ("Behavior-residualized coupling", mechanism["behavior_residualized_coupling"]),
    ]
    for label, item in mechanism_rows:
        lines.append(
            f"| {label} | {_fmt_float(item['mean'])} | "
            f"{item['n_positive']}/{item['n_subjects']} | {_fmt_p(item['sign_flip_p_two_sided'])} |"
        )

    lines.extend(
        [
            "",
            "Interpretation: the intracranial MTL theta-alpha load substrate is the most",
            "stable positive signal. The raw EEGNet-to-MTL coupling is suggestive, but it",
            "weakens after load and task-schedule residualization, so it should remain",
            "exploratory unless a future confirmatory robustness bar is agreed and met.",
            "",
            "## Amendment Guard",
            "",
            f"- Part A: {guard['part_a']}",
            f"- Part B: {guard['part_b']}",
            "",
            "Do not:",
        ]
    )
    lines.extend(f"- {item}" for item in guard["do_not_do"])

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    """CLI entrypoint."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--statistics-summary", required=True, help="Subject statistics JSON summary.")
    ap.add_argument("--behavioral-ablation-summary", required=True, help="Behavioral ablation JSON summary.")
    ap.add_argument("--bandpower-summary", required=True, help="MTL bandpower JSON summary.")
    ap.add_argument("--residual-summary", required=True, help="MTL residual-coupling JSON summary.")
    ap.add_argument("--out-dir", default="outputs/amendment", help="Directory for evidence packet outputs.")
    ap.add_argument("--tag", default=None, help="Optional output tag; defaults from statistics summary.")
    args = ap.parse_args()

    inputs = {
        "statistics_summary": args.statistics_summary,
        "behavioral_ablation_summary": args.behavioral_ablation_summary,
        "bandpower_summary": args.bandpower_summary,
        "residual_summary": args.residual_summary,
    }
    packet = _compile_packet(
        statistics=_load_json(args.statistics_summary),
        ablation=_load_json(args.behavioral_ablation_summary),
        bandpower=_load_json(args.bandpower_summary),
        residual=_load_json(args.residual_summary),
        inputs=inputs,
    )
    tag = args.tag or str(packet["tag"])
    packet["tag"] = tag

    os.makedirs(args.out_dir, exist_ok=True)
    json_path = Path(args.out_dir) / f"phase2_amendment_evidence_{tag}.json"
    md_path = Path(args.out_dir) / f"phase2_amendment_evidence_{tag}.md"

    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(packet, fh, indent=2, default=_json_default, allow_nan=False)
    _write_markdown(str(md_path), packet)

    print(f"Phase 2 amendment evidence packet: {tag}")
    print(f"  headline_success={packet['decoding_boundary']['headline_success']}")
    print(
        "  raw_coupling_p2="
        f"{packet['mechanism_evidence']['raw_score_to_mtl_coupling']['sign_flip_p_two_sided']:.4f}"
    )
    print(
        "  schedule_residual_p2="
        f"{packet['mechanism_evidence']['schedule_residualized_coupling']['sign_flip_p_two_sided']:.4f}"
    )
    print(f"\nWrote:\n  {json_path}\n  {md_path}")


if __name__ == "__main__":
    main()
