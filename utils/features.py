"""Scalp-only feature extraction for working-memory load decoding.

The headline analysis decodes load (high 6/8 vs low 4) from the maintenance period
[-3, 0] s. This module turns aligned scalp epochs into two scalp-derived feature
families on the locked common montage:

  * ``band_power`` -- log-variance per (channel, band) from a zero-phase filter bank.
    Small, interpretable, and the input to the logistic/LDA baseline rung.
  * ``covariance`` -- tangent-space vectorization (``vech`` of the matrix logarithm)
    of the per-band channel covariance. This is the flat, ML-ready representation of
    the symmetric-positive-definite covariance used by the covariance/Riemannian rungs.

Design choices that keep the features honest:
  * Band-pass filtering is applied to the *full* epoch; the maintenance window is then
    sliced from the filtered signal, so filter edge transients never enter the analysis
    window.
  * Filtering is zero-phase (``sosfiltfilt``), so no band introduces a phase delay that
    could shift energy across the window boundary.
  * Covariances are shrunk toward a scaled identity before the matrix log, so the
    representation is well-defined even when a window is rank-deficient.

This module is pure NumPy/SciPy (no NIX dependency): the build script wires the reader
to these functions. Channel order is fixed by the caller (the locked common montage),
so feature columns align across subjects.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.signal import butter, sosfiltfilt

from .epoching import MAINTENANCE_WINDOW_S, time_to_index

# Canonical EEG filter bank (Hz). Upper edge stays below the 100 Hz scalp Nyquist;
# gamma is capped at 45 Hz because scalp gamma above that is dominated by muscle/line
# noise and is not load-informative at 200 Hz.
BANDS: dict[str, tuple[float, float]] = {
    "delta": (1.0, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
    "gamma": (30.0, 45.0),
}

FILTER_ORDER = 4            # per-band Butterworth order (applied zero-phase => effective 2x)
COV_SHRINKAGE = 0.10        # ridge toward scaled identity before the matrix log
_VAR_EPS = 1e-12            # guard for log of a (near-)zero variance


@dataclass
class FeatureBundle:
    """Computed scalp features plus the metadata needed to interpret every column."""
    X: np.ndarray                  # (n_trials, n_features) float32
    feature_names: list[str]       # one per column, e.g. 'bp__C3__theta' / 'cov__C3-C4__alpha'
    feature_family: list[str]      # one per column: 'band_power' | 'covariance'
    cov_matrices: np.ndarray       # (n_trials, n_bands, n_ch, n_ch) shrunk SPD covariances
    channel_names: list[str]
    band_names: list[str]
    trial_axis_len: int            # n_trials (sanity for the caller)


def bandpass_filter(
    data: np.ndarray, low_hz: float, high_hz: float, fs: float, order: int = FILTER_ORDER
) -> np.ndarray:
    """Zero-phase Butterworth band-pass along the last axis.

    Args:
        data: array whose last axis is time, e.g. (n_trials, n_channels, n_samples).
        low_hz, high_hz: band edges in Hz (must satisfy 0 < low < high < fs/2).
        fs: sampling rate in Hz.
        order: Butterworth order (applied forward+backward, so effective order is 2x).

    Returns:
        Filtered array, same shape as ``data``.

    Raises:
        ValueError if the band edges are not a valid sub-Nyquist pass-band.
    """
    nyq = fs / 2.0
    if not (0.0 < low_hz < high_hz < nyq):
        raise ValueError(
            f"Invalid band [{low_hz}, {high_hz}] Hz for fs={fs} Hz (Nyquist {nyq})."
        )
    sos = butter(order, [low_hz, high_hz], btype="band", fs=fs, output="sos")
    return sosfiltfilt(sos, data, axis=-1)


def _vech_index(n: int) -> tuple[np.ndarray, np.ndarray]:
    """Row/col indices of the upper triangle (including diagonal) of an n x n matrix."""
    return np.triu_indices(n)


def _matrix_log_spd(cov: np.ndarray) -> np.ndarray:
    """Batched matrix logarithm of symmetric positive-definite matrices.

    Args:
        cov: (n, k, k) stack of SPD matrices.

    Returns:
        (n, k, k) stack of symmetric matrix logarithms.
    """
    w, V = np.linalg.eigh(cov)
    w = np.clip(w, _VAR_EPS, None)
    logw = np.log(w)
    # V @ diag(logw) @ V^T, batched.
    return (V * logw[:, None, :]) @ np.transpose(V, (0, 2, 1))


def compute_features(
    full_epochs: np.ndarray,
    offset_s: float,
    fs: float,
    channel_names: list[str],
    window_s: tuple[float, float] = MAINTENANCE_WINDOW_S,
    bands: dict[str, tuple[float, float]] = BANDS,
    shrinkage: float = COV_SHRINKAGE,
) -> FeatureBundle:
    """Compute band-power and tangent-space covariance features for one session.

    Filters each band on the full epoch, slices the analysis window from the filtered
    signal, then computes (a) log-variance band power per channel and (b) the
    tangent-space vectorization of the per-band channel covariance.

    Args:
        full_epochs: (n_trials, n_channels, n_samples) aligned epochs, channels already
            restricted and ordered to the common montage by the caller.
        offset_s: time of sample 0 relative to the probe (e.g. -6.0).
        fs: sampling rate in Hz.
        channel_names: channel labels matching ``full_epochs`` axis 1 (montage order).
        window_s: (start_s, end_s) analysis window relative to the probe.
        bands: mapping band name -> (low_hz, high_hz).
        shrinkage: covariance ridge toward a scaled identity, in [0, 1].

    Returns:
        FeatureBundle with the flat feature matrix and per-column provenance.

    Raises:
        ValueError on shape/channel mismatch or an out-of-bounds window.
    """
    if full_epochs.ndim != 3:
        raise ValueError(f"full_epochs must be 3-D (trials, ch, samples); got {full_epochs.shape}.")
    n_trials, n_ch, n_samp = full_epochs.shape
    if n_ch != len(channel_names):
        raise ValueError(
            f"channel_names ({len(channel_names)}) does not match epoch channel axis ({n_ch})."
        )

    i0 = time_to_index(window_s[0], offset_s, fs)
    i1 = time_to_index(window_s[1], offset_s, fs)
    if i0 < 0 or i1 > n_samp or i0 >= i1:
        raise ValueError(
            f"Window {window_s}s -> samples [{i0}, {i1}) out of bounds for {n_samp} samples."
        )

    band_names = list(bands.keys())
    n_bands = len(band_names)
    iu, ju = _vech_index(n_ch)
    n_vech = iu.size

    bp = np.empty((n_trials, n_bands, n_ch), dtype=np.float64)
    cov_all = np.empty((n_trials, n_bands, n_ch, n_ch), dtype=np.float64)
    cov_vech = np.empty((n_trials, n_bands, n_vech), dtype=np.float64)
    eye = np.eye(n_ch)

    for b, name in enumerate(band_names):
        low, high = bands[name]
        win = bandpass_filter(full_epochs.astype(np.float64), low, high, fs)[..., i0:i1]
        # Band power = log variance per channel over the window.
        bp[:, b, :] = np.log(np.var(win, axis=-1) + _VAR_EPS)
        # Channel covariance over the window, shrunk toward a scaled identity.
        wc = win - win.mean(axis=-1, keepdims=True)
        n_win = win.shape[-1]
        cov = np.einsum("tci,tdi->tcd", wc, wc) / (n_win - 1)
        tr = np.einsum("tcc->t", cov) / n_ch
        cov_reg = (1.0 - shrinkage) * cov + shrinkage * tr[:, None, None] * eye
        cov_all[:, b, :, :] = cov_reg
        logc = _matrix_log_spd(cov_reg)
        cov_vech[:, b, :] = logc[:, iu, ju]

    # Assemble the flat feature matrix: band_power block then covariance block.
    bp_flat = bp.reshape(n_trials, n_bands * n_ch)
    cov_flat = cov_vech.reshape(n_trials, n_bands * n_vech)
    X = np.concatenate([bp_flat, cov_flat], axis=1).astype(np.float32)

    feature_names: list[str] = []
    feature_family: list[str] = []
    for name in band_names:
        for ch in channel_names:
            feature_names.append(f"bp__{ch}__{name}")
            feature_family.append("band_power")
    for name in band_names:
        for a, bb in zip(iu, ju):
            tag = channel_names[a] if a == bb else f"{channel_names[a]}-{channel_names[bb]}"
            feature_names.append(f"cov__{tag}__{name}")
            feature_family.append("covariance")

    return FeatureBundle(
        X=X,
        feature_names=feature_names,
        feature_family=feature_family,
        cov_matrices=cov_all.astype(np.float32),
        channel_names=list(channel_names),
        band_names=band_names,
        trial_axis_len=n_trials,
    )
