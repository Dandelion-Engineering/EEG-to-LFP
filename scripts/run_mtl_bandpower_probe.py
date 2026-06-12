"""Probe MTL theta/alpha band power against load and scalp decoder scores.

This is a first mechanism-layer scaffold, not the final coupling claim. It uses the
intracranial recordings only as validation evidence: for the exact trials retained in
the scalp feature bundle, it summarizes maintenance-window MTL theta/alpha power and
asks two conservative questions at the held-out-subject summary level:

1. Does MTL theta/alpha power differ between high-load and low-load trials?
2. Do existing scalp decoder scores track the same MTL summaries within subject?

The output is deliberately descriptive. Directional mechanism success is not declared
here; the Claim Sheet still requires a fuller coupling analysis and agent alignment
before any amendment or claim shift.

Usage:
    .\\venv\\Scripts\\python.exe scripts\\run_mtl_bandpower_probe.py \\
        --data-dir "D:\\Simultaneous EEG_LFP\\data_nix" \\
        --bundle outputs\\features\\feature_bundle.npz \\
        --signal-predictions outputs\\decoding\\predictions_tangent_cov_all.csv \\
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

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import mechanism, nix_io  # noqa: E402
from utils.epoching import MAINTENANCE_WINDOW_S, extract_window  # noqa: E402
from utils.features import BANDS, bandpass_filter  # noqa: E402

_VAR_EPS = 1e-12
REGION_ORDER = ("hippocampus", "amygdala", "parahippocampal")
BAND_ORDER = ("theta", "alpha")


def _derive_tag(path: str) -> str:
    """Derive the run tag from a predictions_<tag>.csv filename."""
    name = Path(path).stem
    prefix = "predictions_"
    return name[len(prefix):] if name.startswith(prefix) else name


def _load_bundle(bundle_path: str) -> pd.DataFrame:
    """Load the bundle trial axis used by scalp decoders."""
    bundle = np.load(bundle_path, allow_pickle=True)
    return pd.DataFrame({
        "trial_id": bundle["trial_id"].astype(str),
        "subject_id": bundle["subject_id"].astype(str),
        "session_id": bundle["session_id"].astype(str),
        "load_binary": bundle["y"].astype(int),
    })


def _load_predictions(path: str, bundle_df: pd.DataFrame) -> pd.DataFrame:
    """Load and validate signal predictions against the bundle trial axis."""
    pred = pd.read_csv(path)
    required = {"trial_id", "subject_id", "session_id", "load_binary", "signal_score", "signal_pred"}
    missing = sorted(required - set(pred.columns))
    if missing:
        raise ValueError(f"Signal prediction file is missing required columns: {missing}")
    if pred["trial_id"].duplicated().any():
        raise ValueError("Signal prediction file contains duplicate trial_id values.")
    missing_pred = sorted(set(bundle_df["trial_id"]) - set(pred["trial_id"]))
    extra_pred = sorted(set(pred["trial_id"]) - set(bundle_df["trial_id"]))
    if missing_pred or extra_pred:
        raise ValueError(
            f"Prediction trials do not match bundle: missing={missing_pred[:5]}, "
            f"extra={extra_pred[:5]}"
        )
    merged = bundle_df.merge(
        pred[["trial_id", "signal_score", "signal_pred", "load_binary"]],
        on="trial_id",
        suffixes=("", "_pred"),
        validate="one_to_one",
    )
    if not np.array_equal(merged["load_binary"].to_numpy(), merged["load_binary_pred"].to_numpy()):
        raise ValueError("Signal prediction load_binary does not match feature bundle labels.")
    return merged.drop(columns=["load_binary_pred"])


def _mtl_contacts_for_session(path: str) -> list[dict]:
    """Return annotated MTL contacts for one NIX session file."""
    return mechanism.mtl_contact_rows(nix_io.read_ieeg_electrode_info(path))


def _band_log_power(data: np.ndarray, offset_s: float, fs: float, band: str) -> np.ndarray:
    """Return log variance per trial/contact in the maintenance window for one band."""
    low, high = BANDS[band]
    filtered = bandpass_filter(data.astype(np.float64), low, high, fs)
    win = extract_window(filtered, offset_s, fs, MAINTENANCE_WINDOW_S)
    return np.log(np.var(win, axis=-1) + _VAR_EPS)


def _safe_mean(values: np.ndarray) -> float:
    """NaN-tolerant mean that returns NaN for empty/all-NaN inputs."""
    if values.size == 0 or np.all(np.isnan(values)):
        return float("nan")
    return float(np.nanmean(values))


def _trial_rows_for_session(path: str, kept_trials: set[str]) -> list[dict]:
    """Compute MTL band-power summaries for kept trials in one session."""
    contacts = _mtl_contacts_for_session(path)
    if not contacts:
        return []
    channels = [row["channel"] for row in contacts]
    epochs = nix_io.load_ieeg_epochs(path, channels=channels, dtype=np.float32)
    kept_idx = [i for i, tid in enumerate(epochs.trial_ids) if tid in kept_trials]
    if not kept_idx:
        return []

    data = epochs.data[kept_idx]
    trial_ids = [epochs.trial_ids[i] for i in kept_idx]
    by_band = {
        band: _band_log_power(data, epochs.offset_s, epochs.sample_rate_hz, band)
        for band in BAND_ORDER
    }
    subregions = np.array([row["mtl_subregion"] for row in contacts])

    rows = []
    for i, trial_id in enumerate(trial_ids):
        row = {
            "trial_id": trial_id,
            "n_mtl_contacts": len(channels),
            "n_hippocampus_contacts": int(np.sum(subregions == "hippocampus")),
            "n_amygdala_contacts": int(np.sum(subregions == "amygdala")),
            "n_parahippocampal_contacts": int(np.sum(subregions == "parahippocampal")),
        }
        for band in BAND_ORDER:
            vals = by_band[band][i]
            row[f"mtl_{band}_log_power"] = _safe_mean(vals)
            for region in REGION_ORDER:
                mask = subregions == region
                row[f"{region}_{band}_log_power"] = _safe_mean(vals[mask])
        row["mtl_theta_alpha_log_power_diff"] = (
            row["mtl_theta_log_power"] - row["mtl_alpha_log_power"]
        )
        rows.append(row)
    return rows


def _zscore(x: np.ndarray) -> np.ndarray:
    """Within-subject z-score with NaNs preserved and zeros for constant inputs."""
    x = x.astype(float)
    out = np.full_like(x, np.nan, dtype=float)
    mask = np.isfinite(x)
    if not np.any(mask):
        return out
    sd = float(np.std(x[mask]))
    if sd <= 0 or np.isnan(sd):
        out[mask] = 0.0
        return out
    out[mask] = (x[mask] - float(np.mean(x[mask]))) / sd
    return out


def _pearson(x: np.ndarray, y: np.ndarray) -> float:
    """Pearson correlation, returning NaN when either vector is constant."""
    mask = np.isfinite(x) & np.isfinite(y)
    if int(mask.sum()) < 3:
        return float("nan")
    xz = _zscore(x[mask])
    yz = _zscore(y[mask])
    if np.allclose(xz, 0.0) or np.allclose(yz, 0.0):
        return float("nan")
    return float(np.mean(xz * yz))


def _load_effect_z(df: pd.DataFrame, col: str) -> float:
    """High-load minus low-load mean after within-subject z-scoring."""
    z = _zscore(df[col].to_numpy(dtype=float))
    labels = df["load_binary"].to_numpy(dtype=int)
    if not np.any(labels == 0) or not np.any(labels == 1):
        return float("nan")
    low = z[labels == 0]
    high = z[labels == 1]
    if not np.any(np.isfinite(low)) or not np.any(np.isfinite(high)):
        return float("nan")
    return float(np.nanmean(high) - np.nanmean(low))


def _subject_summary(trial_df: pd.DataFrame) -> pd.DataFrame:
    """Create one descriptive mechanism row per subject."""
    feature_cols = [
        "mtl_theta_log_power",
        "mtl_alpha_log_power",
        "mtl_theta_alpha_log_power_diff",
        "hippocampus_theta_log_power",
        "hippocampus_alpha_log_power",
        "amygdala_theta_log_power",
        "amygdala_alpha_log_power",
        "parahippocampal_theta_log_power",
        "parahippocampal_alpha_log_power",
    ]
    rows = []
    for subject_id, sdf in trial_df.groupby("subject_id", sort=True):
        row = {
            "subject_id": subject_id,
            "n_trials": int(len(sdf)),
            "n_low": int((sdf["load_binary"] == 0).sum()),
            "n_high": int((sdf["load_binary"] == 1).sum()),
            "n_mtl_contacts": int(sdf["n_mtl_contacts"].max()),
            "signal_score_load_effect_z": _load_effect_z(sdf, "signal_score"),
        }
        score = sdf["signal_score"].to_numpy(dtype=float)
        for col in feature_cols:
            row[f"{col}_load_effect_z"] = _load_effect_z(sdf, col)
            row[f"corr_signal_score_{col}"] = _pearson(score, sdf[col].to_numpy(dtype=float))
        rows.append(row)
    return pd.DataFrame(rows)


def _sign_flip_p_two_sided(values: np.ndarray) -> float:
    """Exact sign-flip p-value for whether the mean differs from zero."""
    vals = values[np.isfinite(values)]
    if len(vals) == 0:
        return float("nan")
    mags = np.abs(vals)
    observed = abs(float(np.mean(vals)))
    null = []
    for signs in itertools.product((-1.0, 1.0), repeat=len(mags)):
        null.append(abs(float(np.mean(mags * np.asarray(signs)))))
    return float(np.mean(np.asarray(null) >= observed))


def _metric_summary(subject_df: pd.DataFrame) -> dict:
    """Summarize subject-level mechanism metrics without declaring success."""
    metrics = [
        "mtl_theta_log_power_load_effect_z",
        "mtl_alpha_log_power_load_effect_z",
        "mtl_theta_alpha_log_power_diff_load_effect_z",
        "corr_signal_score_mtl_theta_log_power",
        "corr_signal_score_mtl_alpha_log_power",
        "corr_signal_score_mtl_theta_alpha_log_power_diff",
    ]
    out = {}
    for metric in metrics:
        values = subject_df[metric].to_numpy(dtype=float)
        finite = values[np.isfinite(values)]
        out[metric] = {
            "n_subjects": int(len(finite)),
            "mean": float(np.mean(finite)) if len(finite) else float("nan"),
            "median": float(np.median(finite)) if len(finite) else float("nan"),
            "n_positive": int(np.sum(finite > 0)),
            "n_negative": int(np.sum(finite < 0)),
            "sign_flip_p_two_sided": _sign_flip_p_two_sided(finite),
        }
    return out


def _json_default(value):
    """Convert NumPy scalars/NaNs for JSON serialization."""
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        value = float(value)
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def _write_markdown(path: str, tag: str, summary: dict, subject_df: pd.DataFrame) -> None:
    """Write a compact human-readable mechanism probe summary."""
    lines = [
        f"# MTL Band-Power Mechanism Probe - {tag}",
        "",
        "> Exploratory mechanism scaffold only. This does not declare the Claim Sheet",
        "> mechanism half supported; it creates the MTL trial/subject summaries needed",
        "> for the fuller coupling analysis.",
        "",
        f"- Trials summarized: {summary['n_trials']}",
        f"- Subjects summarized: {summary['n_subjects']}",
        f"- MTL definition: {', '.join(REGION_ORDER)}",
        f"- Window: maintenance [{MAINTENANCE_WINDOW_S[0]}, {MAINTENANCE_WINDOW_S[1]}) s",
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
        "## Per-Subject Core Readout",
        "",
        "| Subject | Trials | Low | High | MTL contacts | Theta load effect z | "
        "Alpha load effect z | Corr score-theta | Corr score-alpha |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for row in subject_df.itertuples(index=False):
        lines.append(
            f"| {row.subject_id} | {row.n_trials} | {row.n_low} | {row.n_high} | "
            f"{row.n_mtl_contacts} | {row.mtl_theta_log_power_load_effect_z:.3f} | "
            f"{row.mtl_alpha_log_power_load_effect_z:.3f} | "
            f"{row.corr_signal_score_mtl_theta_log_power:.3f} | "
            f"{row.corr_signal_score_mtl_alpha_log_power:.3f} |"
        )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", required=True, help="Directory of Data_Subject_*.h5 files.")
    ap.add_argument("--bundle", required=True, help="feature_bundle.npz path.")
    ap.add_argument("--signal-predictions", required=True, help="predictions_<tag>.csv path.")
    ap.add_argument("--out-dir", default="outputs/mechanism", help="Output directory.")
    ap.add_argument("--tag", default=None, help="Optional output tag.")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    tag = args.tag or _derive_tag(args.signal_predictions)

    bundle_df = _load_bundle(args.bundle)
    trial_axis = _load_predictions(args.signal_predictions, bundle_df)
    kept_trials = set(trial_axis["trial_id"])

    print(f"MTL band-power mechanism probe: {tag}")
    print(f"  kept trials: {len(kept_trials)}")
    trial_rows = []
    files = nix_io.list_session_files(args.data_dir)
    for i, path in enumerate(files, 1):
        rows = _trial_rows_for_session(path, kept_trials)
        trial_rows.extend(rows)
        subj, sess = nix_io.parse_session_filename(path)
        print(f"  [{i:2d}/{len(files)}] {subj}/{sess}: {len(rows)} kept trials summarized")

    mtl_df = pd.DataFrame(trial_rows)
    missing = sorted(kept_trials - set(mtl_df["trial_id"]))
    if missing:
        raise ValueError(f"{len(missing)} kept trials lacked MTL summaries: {missing[:5]}")
    trial_df = trial_axis.merge(mtl_df, on="trial_id", validate="one_to_one")
    trial_df = trial_df.sort_values(["subject_id", "session_id", "trial_id"]).reset_index(drop=True)
    subject_df = _subject_summary(trial_df)
    metric_summary = _metric_summary(subject_df)

    summary = {
        "tag": tag,
        "n_trials": int(len(trial_df)),
        "n_subjects": int(subject_df["subject_id"].nunique()),
        "input_signal_predictions": args.signal_predictions,
        "input_bundle": args.bundle,
        "window_s": list(MAINTENANCE_WINDOW_S),
        "bands_hz": {band: list(BANDS[band]) for band in BAND_ORDER},
        "mtl_definition": mechanism.MTL_REGIONS,
        "metric_summary": metric_summary,
        "interpretation_guard": (
            "Exploratory band-power scaffold only; mechanism success requires fuller "
            "theta-alpha/coupling analysis and agent alignment."
        ),
    }

    trial_path = os.path.join(args.out_dir, f"mtl_bandpower_trial_summary_{tag}.csv")
    subject_path = os.path.join(args.out_dir, f"mtl_bandpower_subject_summary_{tag}.csv")
    json_path = os.path.join(args.out_dir, f"mtl_bandpower_summary_{tag}.json")
    md_path = os.path.join(args.out_dir, f"mtl_bandpower_summary_{tag}.md")
    trial_df.to_csv(trial_path, index=False)
    subject_df.to_csv(subject_path, index=False)
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, default=_json_default, allow_nan=False)
    _write_markdown(md_path, tag, summary, subject_df)

    print("\nCore subject-level means:")
    for metric in (
        "mtl_theta_log_power_load_effect_z",
        "mtl_alpha_log_power_load_effect_z",
        "corr_signal_score_mtl_theta_log_power",
        "corr_signal_score_mtl_alpha_log_power",
    ):
        item = metric_summary[metric]
        print(
            f"  {metric}: mean={item['mean']:.3f}, "
            f"positive={item['n_positive']}/{item['n_subjects']}, "
            f"p2={item['sign_flip_p_two_sided']:.4f}"
        )
    print(f"\nWrote:\n  {trial_path}\n  {subject_path}\n  {json_path}\n  {md_path}")


if __name__ == "__main__":
    main()
