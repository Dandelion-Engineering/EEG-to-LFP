"""Run LOSO ablations for the behavioral-only load control.

The main control harness tests whether scalp signal beats the strongest non-signal
control. This script asks which non-signal behavioral family is carrying that
control by retraining smaller tabular controls on the same held-out-subject folds.

Usage:
    .\\venv\\Scripts\\python.exe scripts\\run_behavioral_control_ablation.py \\
        --bundle outputs\\features\\feature_bundle.npz \\
        --metadata outputs\\features\\feature_metadata.csv \\
        --out-dir outputs\\controls
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score

from run_control_models import (
    BEHAVIORAL_CATEGORICAL,
    BEHAVIORAL_FORBIDDEN,
    BEHAVIORAL_NUMERIC,
    _assert_no_forbidden,
    _select_tabular_C,
    _tabular_pipeline,
)


@dataclass(frozen=True)
class AblationSpec:
    """Column specification for one behavioral-control ablation."""

    name: str
    description: str
    numeric: tuple[str, ...] = ()
    categorical: tuple[str, ...] = ()


ABLATIONS = [
    AblationSpec(
        name="rt_only",
        description="response time only",
        numeric=("response_time_s",),
    ),
    AblationSpec(
        name="correct_match",
        description="correctness plus probe match/mismatch",
        numeric=("correct", "match"),
    ),
    AblationSpec(
        name="previous_trial",
        description="previous-trial correctness only",
        numeric=("previous_trial_correct",),
    ),
    AblationSpec(
        name="trial_index_only",
        description="within-session trial index only",
        numeric=("trial_index",),
    ),
    AblationSpec(
        name="session_only",
        description="session identifier only",
        categorical=("session_id",),
    ),
    AblationSpec(
        name="trial_order_session",
        description="trial index plus session identifier",
        numeric=("trial_index",),
        categorical=("session_id",),
    ),
    AblationSpec(
        name="full_behavioral",
        description="full allowed behavioral control from run_control_models.py",
        numeric=tuple(BEHAVIORAL_NUMERIC),
        categorical=tuple(BEHAVIORAL_CATEGORICAL),
    ),
]


def _load_inputs(bundle_path: str, metadata_path: str) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    """Load bundle-aligned metadata and return trial labels and subjects.

    Args:
        bundle_path: Path to ``feature_bundle.npz``.
        metadata_path: Path to the feature metadata CSV.

    Returns:
        Metadata ordered to the bundle, binary load labels, subject IDs, and trial IDs.

    Raises:
        ValueError: If the metadata cannot be aligned exactly to the bundle trials.
    """
    bundle = np.load(bundle_path, allow_pickle=True)
    trial_id = bundle["trial_id"].astype(str)
    y = bundle["y"].astype(int)
    subject_id = bundle["subject_id"].astype(str)

    meta = pd.read_csv(metadata_path)
    if meta["trial_id"].duplicated().any():
        dup = meta.loc[meta["trial_id"].duplicated(), "trial_id"].head().tolist()
        raise ValueError(f"Metadata has duplicate trial_id values, e.g. {dup}")
    meta = meta.set_index("trial_id").loc[trial_id].reset_index()
    if not np.array_equal(meta["load_binary"].to_numpy(dtype=int), y):
        raise ValueError("Metadata load_binary does not match feature bundle y.")
    return meta, y, subject_id, trial_id


def _validate_specs(meta: pd.DataFrame, specs: list[AblationSpec]) -> None:
    """Validate that ablation columns exist and exclude target encodings."""
    for spec in specs:
        selected = list(spec.numeric) + list(spec.categorical)
        missing = sorted(set(selected) - set(meta.columns))
        if missing:
            raise ValueError(f"{spec.name} is missing metadata columns: {missing}")
        _assert_no_forbidden(selected, BEHAVIORAL_FORBIDDEN, spec.name)


def _fit_one_ablation(
    spec: AblationSpec,
    meta: pd.DataFrame,
    y: np.ndarray,
    subject_id: np.ndarray,
    held_subject: str,
) -> tuple[float, float, np.ndarray, np.ndarray]:
    """Fit one ablation on training subjects and score the held-out subject.

    Args:
        spec: The ablation column specification.
        meta: Bundle-aligned metadata.
        y: Binary load labels.
        subject_id: Subject ID per row.
        held_subject: Subject ID to hold out.

    Returns:
        Balanced accuracy, selected regularization ``C``, predicted labels, and
        positive-class scores for the held-out subject.
    """
    te = subject_id == held_subject
    tr = ~te
    numeric = list(spec.numeric)
    categorical = list(spec.categorical)
    meta_train = meta.loc[tr].reset_index(drop=True)
    meta_test = meta.loc[te].reset_index(drop=True)
    y_train = y[tr]
    y_test = y[te]
    groups_train = subject_id[tr]

    selected_c = _select_tabular_C(meta_train, y_train, groups_train, numeric, categorical)
    model = _tabular_pipeline(numeric, categorical, selected_c)
    model.fit(meta_train, y_train)
    pred = model.predict(meta_test).astype(int)
    score = model.predict_proba(meta_test)[:, 1].astype(float)
    return float(balanced_accuracy_score(y_test, pred)), float(selected_c), pred, score


def _summarize_subject_scores(subject_scores: pd.DataFrame, specs: list[AblationSpec]) -> dict:
    """Build machine-readable summary statistics for each ablation."""
    summary_rows = []
    component_cols = [f"{spec.name}_ba" for spec in specs]
    for spec in specs:
        col = f"{spec.name}_ba"
        vals = subject_scores[col].to_numpy(dtype=np.float64)
        summary_rows.append({
            "component": spec.name,
            "description": spec.description,
            "mean_ba": float(np.mean(vals)),
            "median_ba": float(np.median(vals)),
            "min_ba": float(np.min(vals)),
            "max_ba": float(np.max(vals)),
            "subjects_above_chance": int(np.sum(vals > 0.5)),
        })

    matrix = subject_scores[component_cols].to_numpy(dtype=np.float64)
    best_idx = np.argmax(matrix, axis=1)
    best_counts = pd.Series([specs[i].name for i in best_idx]).value_counts().to_dict()
    return {
        "n_subjects": int(len(subject_scores)),
        "components": summary_rows,
        "best_component_counts": {str(k): int(v) for k, v in best_counts.items()},
    }


def _previous_trial_target_rates(meta: pd.DataFrame) -> list[dict]:
    """Summarize current-load rates by previous-trial correctness."""
    rates = []
    audit = meta[["previous_trial_correct", "load_binary"]].copy()
    audit["previous_trial_correct"] = audit["previous_trial_correct"].fillna("missing").astype(str)
    grouped = audit.groupby("previous_trial_correct", dropna=False)["load_binary"].agg(["count", "mean"])
    for key, row in grouped.reset_index().iterrows():
        rates.append({
            "previous_trial_correct": str(row["previous_trial_correct"]),
            "n_trials": int(row["count"]),
            "high_load_rate": float(row["mean"]),
        })
    return rates


def _write_markdown(summary: dict, subject_scores: pd.DataFrame, specs: list[AblationSpec], path: str) -> None:
    """Write a compact human-readable ablation report."""
    lines = [
        "# Behavioral Control Ablation",
        "",
        "Same LOSO folds and target hygiene as the main control runner.",
        "",
        "| Component | Mean BA | Subjects > 0.50 | Notes |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in summary["components"]:
        lines.append(
            f"| {row['component']} | {row['mean_ba']:.3f} | "
            f"{row['subjects_above_chance']}/{summary['n_subjects']} | {row['description']} |"
        )

    lines.extend([
        "",
        "| Subject | Best component | Best BA | Full behavioral BA |",
        "| --- | --- | ---: | ---: |",
    ])
    for row in subject_scores.itertuples(index=False):
        lines.append(
            f"| {row.subject_id} | {row.best_ablation} | {row.best_ablation_ba:.3f} | "
            f"{getattr(row, 'full_behavioral_ba'):.3f} |"
        )

    if summary.get("previous_trial_correct_target_rates"):
        lines.extend([
            "",
            "## Previous-Trial Target Audit",
            "",
            "| Previous trial correct | Trials | Current high-load rate |",
            "| --- | ---: | ---: |",
        ])
        for row in summary["previous_trial_correct_target_rates"]:
            lines.append(
                f"| {row['previous_trial_correct']} | {row['n_trials']} | "
                f"{row['high_load_rate']:.3f} |"
            )

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    """Parse CLI arguments and run the behavioral-control ablation."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bundle", required=True, help="Path to outputs/features/feature_bundle.npz.")
    ap.add_argument("--metadata", required=True, help="Path to outputs/features/feature_metadata.csv.")
    ap.add_argument("--out-dir", default="outputs/controls", help="Output directory.")
    ap.add_argument("--tag", default="behavioral_ablation", help="Output tag.")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    meta, y, subject_id, trial_id = _load_inputs(args.bundle, args.metadata)
    specs = list(ABLATIONS)
    _validate_specs(meta, specs)

    subjects = sorted(np.unique(subject_id).tolist())
    subject_rows = []
    prediction_parts = []
    print(f"Behavioral ablation run: {args.tag}")
    print(f"  subjects: {len(subjects)}")
    print(f"  components: {', '.join(spec.name for spec in specs)}\n")

    for held in subjects:
        te = subject_id == held
        pred_part = pd.DataFrame({
            "trial_id": trial_id[te],
            "subject_id": subject_id[te],
            "load_binary": y[te],
        })
        row = {"subject_id": held, "n_test": int(te.sum())}
        for spec in specs:
            ba, selected_c, pred, score = _fit_one_ablation(spec, meta, y, subject_id, held)
            row[f"{spec.name}_ba"] = ba
            row[f"{spec.name}_selected_C"] = selected_c
            pred_part[f"{spec.name}_pred"] = pred
            pred_part[f"{spec.name}_score"] = score

        component_cols = [f"{spec.name}_ba" for spec in specs]
        best_col = max(component_cols, key=lambda col: row[col])
        row["best_ablation"] = best_col.removesuffix("_ba")
        row["best_ablation_ba"] = row[best_col]
        row["full_minus_best_single_component"] = (
            row["full_behavioral_ba"]
            - max(row[col] for col in component_cols if col != "full_behavioral_ba")
        )
        subject_rows.append(row)
        prediction_parts.append(pred_part)
        print(
            f"  {held}: best={row['best_ablation']} {row['best_ablation_ba']:.3f}, "
            f"full={row['full_behavioral_ba']:.3f}, rt={row['rt_only_ba']:.3f}"
        )

    subject_scores = pd.DataFrame(subject_rows)
    predictions = pd.concat(prediction_parts, ignore_index=True)
    summary = _summarize_subject_scores(subject_scores, specs)
    summary["previous_trial_correct_target_rates"] = _previous_trial_target_rates(meta)

    subject_path = os.path.join(args.out_dir, f"{args.tag}_subject_scores.csv")
    pred_path = os.path.join(args.out_dir, f"{args.tag}_predictions.csv")
    json_path = os.path.join(args.out_dir, f"{args.tag}_summary.json")
    md_path = os.path.join(args.out_dir, f"{args.tag}_summary.md")

    subject_scores.to_csv(subject_path, index=False)
    predictions.to_csv(pred_path, index=False)
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
    _write_markdown(summary, subject_scores, specs, md_path)

    print("\nMean balanced accuracy by component:")
    for row in summary["components"]:
        print(f"  {row['component']}: {row['mean_ba']:.3f}")
    print(f"\nWrote:\n  {subject_path}\n  {pred_path}\n  {json_path}\n  {md_path}")


if __name__ == "__main__":
    main()
