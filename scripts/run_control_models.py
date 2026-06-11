"""Run LOSO non-signal controls for the working-memory load decoder.

This script consumes Claude's scalp feature bundle plus a signal-model prediction file
and emits the control side of Codex's evaluation contract:

* label-shuffle control using the same scalp feature columns as the signal model;
* behavioral-only control with target-encoding columns forbidden;
* timing-only control with response/behavioral/signal columns forbidden;
* within-training subject-identity diagnostic from signal features.

All controls use the same leave-one-subject-out folds as the signal model. Any model
selection happens inside the training subjects only; the held-out subject is scored
once.

Usage:
    .\\venv\\Scripts\\python.exe scripts\\run_control_models.py \\
        --bundle outputs\\features\\feature_bundle.npz \\
        --metadata outputs\\features\\feature_metadata.csv \\
        --signal-predictions outputs\\decoding\\predictions_logistic_all_all.csv \\
        --signal-subject-scores outputs\\decoding\\subject_scores_logistic_all_all.csv \\
        --out-dir outputs\\controls
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd
import warnings

from sklearn.compose import ColumnTransformer
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import GroupKFold, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

C_GRID = [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0]

BEHAVIORAL_NUMERIC = [
    "response_time_s",
    "correct",
    "match",
    "trial_index",
    "previous_trial_correct",
]
BEHAVIORAL_CATEGORICAL = ["session_id"]

TIMING_NUMERIC = [
    "trial_index",
    "fixation_onset_s",
    "encoding_onset_s",
    "maintenance_onset_s",
    "maintenance_offset_s",
    "probe_onset_s",
]
TIMING_CATEGORICAL = ["session_id"]

BEHAVIORAL_FORBIDDEN = {
    "set_size",
    "load_binary",
    "stimulus_count",
    "memory_list_length",
    "probe_letter",
}
TIMING_FORBIDDEN = BEHAVIORAL_FORBIDDEN | {
    "response_time_s",
    "response_onset_s",
    "correct",
    "match",
    "response",
    "previous_trial_correct",
}


def _derive_tag(path: str) -> str:
    """Derive the run tag from a predictions_<tag>.csv filename."""
    name = Path(path).stem
    return name[len("predictions_"):] if name.startswith("predictions_") else name


def _select_signal_columns(bundle, feature_family: str, channel_set: str) -> np.ndarray:
    """Return feature columns for the requested signal family/channel set.

    Args:
        bundle: loaded feature_bundle.npz.
        feature_family: ``band_power``, ``covariance``, or ``all``.
        channel_set: ``all`` for the locked 8-channel montage or ``brain`` to exclude
            A1/A2 reference channels.

    Returns:
        Array of selected column indices.

    Raises:
        ValueError if no feature column matches the requested configuration.
    """
    families = bundle["feature_family"].astype(str)
    names = bundle["feature_names"].astype(str)
    channel_names = bundle["channel_names"].astype(str)
    channel_role = bundle["channel_role"].astype(str)

    if channel_set == "brain":
        kept_channels = {c for c, r in zip(channel_names, channel_role) if r == "brain"}
    else:
        kept_channels = set(channel_names)

    cols: list[int] = []
    for j, (name, family) in enumerate(zip(names, families)):
        if feature_family != "all" and family != feature_family:
            continue
        token = name.split("__")[1]
        channels = token.split("-")
        if all(ch in kept_channels for ch in channels):
            cols.append(j)
    if not cols:
        raise ValueError(
            f"No signal feature columns match family={feature_family}, channel_set={channel_set}."
        )
    return np.array(cols, dtype=int)


def _available_columns(meta: pd.DataFrame, cols: list[str], label: str) -> list[str]:
    """Return available columns and fail if none are available."""
    found = [c for c in cols if c in meta.columns]
    if not found:
        raise ValueError(f"No available {label} columns among requested set: {cols}")
    return found


def _assert_no_forbidden(selected: list[str], forbidden: set[str], control_name: str) -> None:
    """Fail loudly if a control design includes target-encoding forbidden columns."""
    bad = sorted(set(selected) & forbidden)
    if bad:
        raise ValueError(f"{control_name} selected forbidden columns: {bad}")


def _tabular_pipeline(numeric_cols: list[str], categorical_cols: list[str], C: float) -> Pipeline:
    """Build a logistic tabular classifier with train-only preprocessing."""
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    pre = ColumnTransformer(
        [
            ("num", numeric, numeric_cols),
            ("cat", categorical, categorical_cols),
        ],
        remainder="drop",
    )
    return Pipeline([
        ("pre", pre),
        ("clf", LogisticRegression(C=C, solver="liblinear", max_iter=2000)),
    ])


def _make_signal_model(model_name: str, C: float | None):
    """Construct the signal-space model used by the label-shuffle control."""
    if model_name == "logistic":
        return LogisticRegression(
            C=1.0 if C is None else float(C), solver="liblinear", max_iter=2000
        )
    if model_name == "lda":
        return LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")
    raise ValueError(f"Unknown model '{model_name}' (use logistic or lda).")


def _select_tabular_C(
    meta_train: pd.DataFrame,
    y_train: np.ndarray,
    groups_train: np.ndarray,
    numeric_cols: list[str],
    categorical_cols: list[str],
) -> float:
    """Select logistic C by inner subject-grouped CV on training subjects only."""
    n_groups = len(np.unique(groups_train))
    n_splits = min(5, n_groups)
    gkf = GroupKFold(n_splits=n_splits)
    best_C, best_score = C_GRID[0], -np.inf
    for C in C_GRID:
        fold_scores = []
        for inner_train, inner_test in gkf.split(meta_train, y_train, groups_train):
            pipe = _tabular_pipeline(numeric_cols, categorical_cols, C)
            pipe.fit(meta_train.iloc[inner_train], y_train[inner_train])
            pred = pipe.predict(meta_train.iloc[inner_test])
            fold_scores.append(balanced_accuracy_score(y_train[inner_test], pred))
        score = float(np.mean(fold_scores))
        if score > best_score:
            best_C, best_score = C, score
    return best_C


def _shuffle_labels_within_training_strata(
    y_train: np.ndarray,
    subject_train: np.ndarray,
    session_train: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Shuffle labels inside subject/session strata where possible.

    If a session has only one class, rows from such sessions are pooled within the same
    subject and shuffled there. Labels never move across subjects.
    """
    shuffled = np.array(y_train, copy=True)
    for subject in np.unique(subject_train):
        subject_idx = np.where(subject_train == subject)[0]
        fallback: list[int] = []
        for session in np.unique(session_train[subject_idx]):
            idx = subject_idx[session_train[subject_idx] == session]
            if len(np.unique(y_train[idx])) > 1:
                shuffled[idx] = rng.permutation(y_train[idx])
            else:
                fallback.extend(idx.tolist())
        if len(fallback) > 1:
            fb = np.array(fallback, dtype=int)
            shuffled[fb] = rng.permutation(y_train[fb])
    return shuffled


def _signal_scores(model, X_test: np.ndarray) -> np.ndarray:
    """Return positive-class scores for classifiers with either proba or decision output."""
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X_test)[:, 1]
    return model.decision_function(X_test)


def _subject_identity_diagnostic(
    X_train: np.ndarray,
    subject_train: np.ndarray,
    seed: int,
) -> float:
    """Estimate how separable training subjects are from signal features."""
    counts = pd.Series(subject_train).value_counts()
    n_splits = min(3, int(counts.min()))
    if n_splits < 2:
        return float("nan")
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    scores = []
    for tr, te in cv.split(X_train, subject_train):
        pipe = Pipeline([
            ("scaler", StandardScaler()),
            (
                "clf",
                LogisticRegression(
                    C=1.0,
                    solver="lbfgs",
                    max_iter=2000,
                    class_weight="balanced",
                ),
            ),
        ])
        pipe.fit(X_train[tr], subject_train[tr])
        pred = pipe.predict(X_train[te])
        scores.append(balanced_accuracy_score(subject_train[te], pred))
    return float(np.mean(scores))


def _load_inputs(args):
    """Load bundle, metadata, and signal predictions; validate one row per trial."""
    bundle = np.load(args.bundle, allow_pickle=True)
    trial_id = bundle["trial_id"].astype(str)
    y = bundle["y"].astype(int)
    subject_id = bundle["subject_id"].astype(str)
    session_id = bundle["session_id"].astype(str)

    meta = pd.read_csv(args.metadata)
    if meta["trial_id"].duplicated().any():
        dup = meta.loc[meta["trial_id"].duplicated(), "trial_id"].head().tolist()
        raise ValueError(f"Metadata has duplicate trial_id values, e.g. {dup}")
    meta = meta.set_index("trial_id").loc[trial_id].reset_index()
    if not np.array_equal(meta["load_binary"].to_numpy(dtype=int), y):
        raise ValueError("Metadata load_binary does not match feature bundle y.")

    signal_pred = pd.read_csv(args.signal_predictions)
    required_signal = {"trial_id", "signal_pred", "signal_score", "load_binary"}
    missing = sorted(required_signal - set(signal_pred.columns))
    if missing:
        raise ValueError(f"Signal predictions missing required columns: {missing}")
    if signal_pred["trial_id"].duplicated().any():
        raise ValueError("Signal predictions have duplicate trial_id rows.")
    signal_pred = signal_pred.set_index("trial_id").loc[trial_id].reset_index()
    if not np.array_equal(signal_pred["load_binary"].to_numpy(dtype=int), y):
        raise ValueError("Signal prediction load_binary does not match feature bundle y.")

    signal_scores = pd.read_csv(args.signal_subject_scores)
    if "subject_id" not in signal_scores.columns or "signal_ba" not in signal_scores.columns:
        raise ValueError("Signal subject score file must contain subject_id and signal_ba.")
    signal_scores = signal_scores.set_index("subject_id")

    return bundle, meta, signal_pred, signal_scores, trial_id, y, subject_id, session_id


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bundle", required=True, help="Path to outputs/features/feature_bundle.npz.")
    ap.add_argument("--metadata", required=True, help="Path to outputs/features/feature_metadata.csv.")
    ap.add_argument("--signal-predictions", required=True, help="Signal predictions_<tag>.csv.")
    ap.add_argument("--signal-subject-scores", required=True, help="Signal subject_scores_<tag>.csv.")
    ap.add_argument("--out-dir", default="outputs/controls", help="Output directory.")
    ap.add_argument("--model", choices=["logistic", "lda"], default="logistic")
    ap.add_argument("--feature-family", choices=["band_power", "covariance", "all"], default="all")
    ap.add_argument("--channel-set", choices=["all", "brain"], default="all")
    ap.add_argument("--n-shuffles", type=int, default=100, help="Label-shuffle fits per LOSO fold.")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", default=None, help="Optional output tag; defaults to signal filename tag.")
    args = ap.parse_args()

    if args.n_shuffles < 1:
        raise ValueError("--n-shuffles must be >= 1.")
    warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")
    os.makedirs(args.out_dir, exist_ok=True)

    tag = args.tag or _derive_tag(args.signal_predictions)
    (
        bundle,
        meta,
        signal_pred,
        signal_scores,
        trial_id,
        y,
        subject_id,
        session_id,
    ) = _load_inputs(args)

    behavioral_numeric = _available_columns(meta, BEHAVIORAL_NUMERIC, "behavioral numeric")
    behavioral_categorical = _available_columns(meta, BEHAVIORAL_CATEGORICAL, "behavioral categorical")
    timing_numeric = _available_columns(meta, TIMING_NUMERIC, "timing numeric")
    timing_categorical = _available_columns(meta, TIMING_CATEGORICAL, "timing categorical")
    _assert_no_forbidden(behavioral_numeric + behavioral_categorical, BEHAVIORAL_FORBIDDEN, "behavioral")
    _assert_no_forbidden(timing_numeric + timing_categorical, TIMING_FORBIDDEN, "timing")

    X_signal = bundle["X_signal"][:, _select_signal_columns(bundle, args.feature_family, args.channel_set)]
    rng = np.random.default_rng(args.seed)
    subjects = sorted(np.unique(subject_id).tolist())
    signal_C = {}
    if "selected_C" in signal_scores.columns:
        signal_C = signal_scores["selected_C"].to_dict()

    prediction_parts = []
    subject_rows = []
    print(f"Control run: {tag}")
    print(f"  signal feature matrix for shuffle: {X_signal.shape}")
    print(f"  behavioral columns: {behavioral_numeric + behavioral_categorical}")
    print(f"  timing columns: {timing_numeric + timing_categorical}")
    print(f"  label shuffles per fold: {args.n_shuffles}\n")

    for held in subjects:
        te = subject_id == held
        tr = ~te
        y_train, y_test = y[tr], y[te]
        meta_train, meta_test = meta.loc[tr].reset_index(drop=True), meta.loc[te].reset_index(drop=True)
        groups_train = subject_id[tr]

        beh_C = _select_tabular_C(
            meta_train, y_train, groups_train, behavioral_numeric, behavioral_categorical
        )
        beh_model = _tabular_pipeline(behavioral_numeric, behavioral_categorical, beh_C)
        beh_model.fit(meta_train, y_train)
        beh_pred = beh_model.predict(meta_test)
        beh_score = beh_model.predict_proba(meta_test)[:, 1]
        behavioral_ba = balanced_accuracy_score(y_test, beh_pred)

        timing_C = _select_tabular_C(meta_train, y_train, groups_train, timing_numeric, timing_categorical)
        timing_model = _tabular_pipeline(timing_numeric, timing_categorical, timing_C)
        timing_model.fit(meta_train, y_train)
        timing_pred = timing_model.predict(meta_test)
        timing_score = timing_model.predict_proba(meta_test)[:, 1]
        timing_ba = balanced_accuracy_score(y_test, timing_pred)

        shuffle_ba = []
        shuffle_score_sum = np.zeros(te.sum(), dtype=np.float64)
        shuffle_pred_sum = np.zeros(te.sum(), dtype=np.float64)
        signal_scaler = StandardScaler().fit(X_signal[tr])
        X_signal_train = signal_scaler.transform(X_signal[tr])
        X_signal_test = signal_scaler.transform(X_signal[te])
        for _ in range(args.n_shuffles):
            y_shuf = _shuffle_labels_within_training_strata(
                y_train,
                subject_id[tr],
                session_id[tr],
                rng,
            )
            model = _make_signal_model(args.model, signal_C.get(held))
            model.fit(X_signal_train, y_shuf)
            pred = model.predict(X_signal_test)
            score = _signal_scores(model, X_signal_test)
            shuffle_ba.append(balanced_accuracy_score(y_test, pred))
            shuffle_score_sum += score
            shuffle_pred_sum += pred

        shuffle_ba_arr = np.asarray(shuffle_ba, dtype=np.float64)
        shuffle_score_mean = shuffle_score_sum / args.n_shuffles
        shuffle_pred_rate = shuffle_pred_sum / args.n_shuffles
        shuffle_pred_majority = (shuffle_pred_rate >= 0.5).astype(int)

        subj_signal = float(signal_scores.loc[held, "signal_ba"])
        identity_ba = _subject_identity_diagnostic(X_signal[tr], subject_id[tr], args.seed)

        subject_rows.append({
            "subject_id": held,
            "n_test": int(te.sum()),
            "signal_ba": subj_signal,
            "behavioral_ba": float(behavioral_ba),
            "timing_ba": float(timing_ba),
            "label_shuffle_ba_mean": float(np.mean(shuffle_ba_arr)),
            "label_shuffle_ba_p05": float(np.quantile(shuffle_ba_arr, 0.05)),
            "label_shuffle_ba_p95": float(np.quantile(shuffle_ba_arr, 0.95)),
            "label_shuffle_ba_max": float(np.max(shuffle_ba_arr)),
            "behavioral_selected_C": beh_C,
            "timing_selected_C": timing_C,
            "label_shuffle_n": args.n_shuffles,
            "subject_identity_cv_ba": identity_ba,
        })

        part = signal_pred.loc[te].copy()
        part["set_size"] = meta.loc[te, "set_size"].to_numpy()
        part["behavioral_pred"] = beh_pred.astype(int)
        part["behavioral_score"] = beh_score.astype(float)
        part["timing_pred"] = timing_pred.astype(int)
        part["timing_score"] = timing_score.astype(float)
        part["label_shuffle_pred"] = shuffle_pred_majority.astype(int)
        part["label_shuffle_score_mean"] = shuffle_score_mean.astype(float)
        part["label_shuffle_pred_rate"] = shuffle_pred_rate.astype(float)
        prediction_parts.append(part)

        print(
            f"  {held}: signal={subj_signal:.3f}, behavioral={behavioral_ba:.3f}, "
            f"timing={timing_ba:.3f}, shuffle_mean={np.mean(shuffle_ba_arr):.3f}, "
            f"id_diag={identity_ba:.3f}"
        )

    predictions = pd.concat(prediction_parts, ignore_index=True)
    subject_scores = pd.DataFrame(subject_rows)

    pred_path = os.path.join(args.out_dir, f"control_predictions_{tag}.csv")
    score_path = os.path.join(args.out_dir, f"control_subject_scores_{tag}.csv")
    predictions.to_csv(pred_path, index=False)
    subject_scores.to_csv(score_path, index=False)

    print(f"\nWrote:\n  {pred_path}\n  {score_path}")


if __name__ == "__main__":
    main()
