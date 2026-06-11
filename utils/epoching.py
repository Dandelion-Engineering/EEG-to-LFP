"""Cut analysis windows from aligned epochs.

The headline analysis decodes working-memory load from the *maintenance* period,
which the dataset fixes at [-3, 0] s relative to the probe (verified constant across
set sizes and subjects). This module turns a (trial, channel, sample) epoch array
plus its time reference into a windowed sub-array, and records the window definition
so downstream feature/leakage code can stay honest about what was used.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Predeclared headline window (s, probe == 0). Maintenance onset is -3 s; probe is 0 s.
MAINTENANCE_WINDOW_S = (-3.0, 0.0)


@dataclass
class WindowSpec:
    """A named analysis window in seconds relative to the probe (probe == 0)."""
    name: str
    t_start_s: float
    t_end_s: float


def time_to_index(t_s: float, offset_s: float, sample_rate_hz: float) -> int:
    """Convert a time (s, probe==0) to the nearest sample index in a data array.

    Args:
        t_s: target time in seconds.
        offset_s: time of sample 0 (e.g. -6.0 for this dataset).
        sample_rate_hz: sampling rate.

    Returns:
        Integer sample index (rounded to nearest sample).
    """
    return int(round((t_s - offset_s) * sample_rate_hz))


def extract_window(
    data: np.ndarray,
    offset_s: float,
    sample_rate_hz: float,
    window: WindowSpec | tuple[float, float],
) -> np.ndarray:
    """Slice a window out of a (..., n_samples) epoch array along the last axis.

    Args:
        data: array whose last axis is time, e.g. (n_trials, n_channels, n_samples).
        offset_s: time of sample 0 relative to the probe.
        sample_rate_hz: sampling rate of ``data``.
        window: WindowSpec or (t_start_s, t_end_s). Half-open [start, end).

    Returns:
        A view/sub-array covering [t_start, t_end) along the last axis.

    Raises:
        ValueError if the requested window falls outside the array bounds.
    """
    if isinstance(window, WindowSpec):
        t0, t1 = window.t_start_s, window.t_end_s
    else:
        t0, t1 = window
    i0 = time_to_index(t0, offset_s, sample_rate_hz)
    i1 = time_to_index(t1, offset_s, sample_rate_hz)
    n = data.shape[-1]
    if i0 < 0 or i1 > n or i0 >= i1:
        raise ValueError(
            f"Window [{t0}, {t1}) s -> samples [{i0}, {i1}) is out of bounds for "
            f"an array with {n} samples (offset {offset_s}s, {sample_rate_hz}Hz)."
        )
    return data[..., i0:i1]


def maintenance_window(sample_rate_hz: float, offset_s: float) -> WindowSpec:
    """Return the predeclared maintenance WindowSpec (provided for symmetry/clarity)."""
    return WindowSpec("maintenance", MAINTENANCE_WINDOW_S[0], MAINTENANCE_WINDOW_S[1])
