"""Residualized MTL coupling sensitivity check for scalp decoder scores.

This script is a mechanism-layer sensitivity probe, not a Claim Sheet success test.
It consumes the trial-level output from ``run_mtl_bandpower_probe.py`` and asks whether
the fixed EEGNet mechanism metric

    corr(signal_score, MTL theta-alpha log-power difference)

survives increasingly strict within-subject residualization. The raw correlation is
useful, but both the scalp decoder score and MTL theta-alpha power can move with the
high-vs-low load label. Residualized views separate the exploratory coupling signal from
shared label and task-schedule structure.

Usage:
    .\\venv\\Scripts\\python.exe scripts\\run_mtl_residual_coupling_probe.py \\
        --trial-summary outputs\\mechanism\\mtl_bandpower_trial_summary_eegnet_raw_all.csv \\
        --metadata outputs\\features\\feature_metadata.csv \\
        --out-dir outputs\\mechanism
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd


TARGET_MTL_COLUMN = "mtl_theta_alpha_log_power_diff"


def _derive_tag(path: str) -> str:
    """Derive a run tag from ``mtl_bandpower_trial_summary_<tag>.csv``."""
    stem = Path(path).stem
    prefix = "mtl_bandpower_trial_summary_"
    return stem[len(prefix):] if stem.startswith(prefix) else stem


def _zscore(values: np.ndarray) -> np.ndarray:
    """Return a finite-value z-score, preserving NaNs."""
    x = np.asarray(values, dtype=float)
    out = np.full(len(x), np.nan, dtype=float)
    mask = np.isfinite(x)
    if not np.any(mask):
        return out
    sd = float(np.std(x[mask]))
    if sd <= 0.0 or not np.isfinite(sd):
        out[mask] = 0.0
    else:
        out[mask] = (x[mask] - float(np.mean(x[mask]))) / sd
    return out


def _dummy_matrix(values: pd.Series, prefix: str) -> tuple[np.ndarray, list[str]]:
    """Return drop-first one-hot columns for a categorical series."""
    dummies = pd.get_dummies(values.astype(str), prefix=prefix, drop_first=True)
    return dummies.to_numpy(dtype=float), dummies.columns.astype(str).tolist()


def _residualize(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Residualize ``y`` on design matrix ``x`` with an intercept."""
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    mask = np.isfinite(y) & np.all(np.isfinite(x), axis=1)
    out = np.full(len(y), np.nan, dtype=float)
    if int(mask.sum()) < x.shape[1] + 3:
        return out
    design = np.c_[np.ones(int(mask.sum())), x[mask]]
    beta = np.linalg.lstsq(design, y[mask], rcond=None)[0]
    out[mask] = y[mask] - design @ beta
    return out


def _pearson(x: np.ndarray, y: np.ndarray) -> float:
    """Pearson correlation with NaN/constant guards."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    if int(mask.sum()) < 3:
        return float("nan")
    x = x[mask]
    y = y[mask]
    if float(np.std(x)) <= 0.0 or float(np.std(y)) <= 0.0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def _sign_flip_p_two_sided(values: np.ndarray) -> float:
    """Exact subject-level sign-flip p-value for mean != 0."""
    vals = np.asarray(values, dtype=float)
    vals = vals[np.isfinite(vals)]
    if len(vals) == 0:
        return float("nan")
    mags = np.abs(vals)
    observed = abs(float(np.mean(vals)))
    null = []
    for signs in itertools.product((-1.0, 1.0), repeat=len(mags)):
        null.append(abs(float(np.mean(mags * np.asarray(signs)))))
    return float(np.mean(np.asarray(null) >= observed))


def _metric_summary(subject_df: pd.DataFrame) -> dict:
    """Summarize every subject-level correlation column."""
    out = {}
    for col in [c for c in subject_df.columns if c.startswith("corr_")]:
        values = subject_df[col].to_numpy(dtype=float)
        finite = values[np.isfinite(values)]
        out[col] = {
            "n_subjects": int(len(finite)),
            "mean": float(np.mean(finite)) if len(finite) else float("nan"),
            "median": float(np.median(finite)) if len(finite) else float("nan"),
            "n_positive": int(np.sum(finite > 0.0)),
            "n_negative": int(np.sum(finite < 0.0)),
            "sign_flip_p_two_sided": _sign_flip_p_two_sided(finite),
        }
    return out


def _subject_designs(sdf: pd.DataFrame) -> dict[str, tuple[np.ndarray, list[str]]]:
    """Build nested residualization designs for one subject."""
    load = sdf[["load_binary"]].to_numpy(dtype=float)

    previous = sdf["previous_trial_correct"].fillna(-1.0).to_numpy(dtype=float)[:, None]
    previous_missing = sdf["previous_trial_correct"].isna().astype(float).to_numpy()[:, None]
    trial_index_z = _zscore(sdf["trial_index"].to_numpy(dtype=float))[:, None]
    session_x, session_cols = _dummy_matrix(sdf["session_id"], "session")

    response_time_z = _zscore(sdf["response_time_s"].to_numpy(dtype=float))[:, None]
    correct = sdf["correct"].to_numpy(dtype=float)[:, None]
    match = sdf["match"].to_numpy(dtype=float)[:, None]

    designs: dict[str, tuple[np.ndarray, list[str]]] = {
        "load": (load, ["load_binary"]),
        "schedule": (
            np.c_[load, previous, previous_missing, trial_index_z, session_x],
            ["load_binary", "previous_trial_correct", "previous_trial_missing", "trial_index_z"]
            + session_cols,
        ),
        "behavior": (
            np.c_[load, previous, previous_missing, trial_index_z, session_x, correct, match, response_time_z],
            ["load_binary", "previous_trial_correct", "previous_trial_missing", "trial_index_z"]
            + session_cols
            + ["correct", "match", "response_time_z"],
        ),
    }
    return designs


def _load_inputs(trial_summary: str, metadata: str) -> pd.DataFrame:
    """Load and validate trial-level mechanism and metadata tables."""
    trial = pd.read_csv(trial_summary)
    meta = pd.read_csv(metadata)
    required_trial = {
        "trial_id",
        "subject_id",
        "session_id",
        "load_binary",
        "signal_score",
        TARGET_MTL_COLUMN,
    }
    required_meta = {
        "trial_id",
        "previous_trial_correct",
        "trial_index",
        "response_time_s",
        "correct",
        "match",
    }
    missing_trial = sorted(required_trial - set(trial.columns))
    missing_meta = sorted(required_meta - set(meta.columns))
    if missing_trial:
        raise ValueError(f"Trial summary missing required columns: {missing_trial}")
    if missing_meta:
        raise ValueError(f"Metadata missing required columns: {missing_meta}")
    if trial["trial_id"].duplicated().any():
        raise ValueError("Trial summary contains duplicate trial_id values.")
    if meta["trial_id"].duplicated().any():
        raise ValueError("Metadata contains duplicate trial_id values.")

    merged = trial.merge(meta[list(required_meta)], on="trial_id", how="left", validate="one_to_one")
    if merged[list(required_meta - {"trial_id"})].isna().all(axis=None):
        raise ValueError("Metadata merge failed; no covariates were attached.")
    return merged.sort_values(["subject_id", "session_id", "trial_id"]).reset_index(drop=True)


def _subject_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Compute raw and residualized score-MTL correlations per subject."""
    rows = []
    for subject_id, sdf in df.groupby("subject_id", sort=True):
        score = sdf["signal_score"].to_numpy(dtype=float)
        mtl = sdf[TARGET_MTL_COLUMN].to_numpy(dtype=float)
        row = {
            "subject_id": subject_id,
            "n_trials": int(len(sdf)),
            "n_low": int((sdf["load_binary"] == 0).sum()),
            "n_high": int((sdf["load_binary"] == 1).sum()),
            "corr_raw_score_mtl_theta_alpha_diff": _pearson(score, mtl),
        }
        for name, (design, cols) in _subject_designs(sdf).items():
            score_resid = _residualize(score, design)
            mtl_resid = _residualize(mtl, design)
            row[f"corr_{name}_residual_score_mtl_theta_alpha_diff"] = _pearson(
                score_resid, mtl_resid
            )
            row[f"{name}_residual_covariates"] = ";".join(cols)
        rows.append(row)
    return pd.DataFrame(rows)


def _json_default(value):
    """Convert NumPy values for strict JSON serialization."""
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        value = float(value)
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def _write_markdown(path: str, tag: str, summary: dict, subject_df: pd.DataFrame) -> None:
    """Write a compact mechanism sensitivity report."""
    lines = [
        f"# MTL Residual Coupling Probe - {tag}",
        "",
        "> Sensitivity analysis only. These rows do not declare mechanism success;",
        "> they show how the fixed EEGNet score/MTL theta-alpha relationship changes",
        "> after removing load and task-schedule covariates within subject.",
        "",
        f"- Trials analyzed: {summary['n_trials']}",
        f"- Subjects analyzed: {summary['n_subjects']}",
        f"- Fixed MTL metric: `{TARGET_MTL_COLUMN}`",
        "",
        "## Subject-Level Metrics",
        "",
        "| Metric | Mean | Median | Positive | Two-sided sign-flip p |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for metric, item in summary["metric_summary"].items():
        lines.append(
            f"| `{metric}` | {item['mean']:.3f} | {item['median']:.3f} | "
            f"{item['n_positive']}/{item['n_subjects']} | {item['sign_flip_p_two_sided']:.4f} |"
        )
    lines.extend([
        "",
        "## Interpretation Guard",
        "",
        "The raw EEGNet score-to-MTL theta-alpha correlation is the exploratory mechanism",
        "signal. Residualized rows ask whether that relationship remains after accounting",
        "for the target label and task-schedule covariates. A weaker residual result means",
        "the mechanism claim should be framed as suggestive unless a separately specified",
        "confirmatory analysis clears its own bar.",
        "",
        "## Per-Subject Readout",
        "",
        "| Subject | Trials | Raw | Load resid | Schedule resid | Behavior resid |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ])
    for row in subject_df.itertuples(index=False):
        lines.append(
            f"| {row.subject_id} | {row.n_trials} | "
            f"{row.corr_raw_score_mtl_theta_alpha_diff:.3f} | "
            f"{row.corr_load_residual_score_mtl_theta_alpha_diff:.3f} | "
            f"{row.corr_schedule_residual_score_mtl_theta_alpha_diff:.3f} | "
            f"{row.corr_behavior_residual_score_mtl_theta_alpha_diff:.3f} |"
        )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    """CLI entrypoint."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trial-summary", required=True, help="mtl_bandpower_trial_summary_<tag>.csv path.")
    ap.add_argument("--metadata", required=True, help="Feature metadata CSV with behavioral covariates.")
    ap.add_argument("--out-dir", default="outputs/mechanism", help="Output directory.")
    ap.add_argument("--tag", default=None, help="Optional output tag; defaults from trial-summary filename.")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    tag = args.tag or _derive_tag(args.trial_summary)
    df = _load_inputs(args.trial_summary, args.metadata)
    subject_df = _subject_rows(df)
    summary = {
        "tag": tag,
        "n_trials": int(len(df)),
        "n_subjects": int(subject_df["subject_id"].nunique()),
        "input_trial_summary": args.trial_summary,
        "input_metadata": args.metadata,
        "target_mtl_column": TARGET_MTL_COLUMN,
        "metric_summary": _metric_summary(subject_df),
        "interpretation_guard": (
            "Sensitivity analysis only; residualized coupling weakens the exploratory "
            "mechanism result and should not be converted into a confirmed mechanism "
            "claim without an agreed confirmatory bar."
        ),
    }

    subject_path = os.path.join(args.out_dir, f"mtl_residual_coupling_subject_summary_{tag}.csv")
    json_path = os.path.join(args.out_dir, f"mtl_residual_coupling_summary_{tag}.json")
    md_path = os.path.join(args.out_dir, f"mtl_residual_coupling_summary_{tag}.md")
    subject_df.to_csv(subject_path, index=False)
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, default=_json_default, allow_nan=False)
    _write_markdown(md_path, tag, summary, subject_df)

    print(f"MTL residual coupling probe: {tag}")
    for metric, item in summary["metric_summary"].items():
        print(
            f"  {metric}: mean={item['mean']:.3f}, "
            f"positive={item['n_positive']}/{item['n_subjects']}, "
            f"p2={item['sign_flip_p_two_sided']:.4f}"
        )
    print(f"\nWrote:\n  {subject_path}\n  {json_path}\n  {md_path}")


if __name__ == "__main__":
    main()
