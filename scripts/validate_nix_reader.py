"""Stop-or-go validation gate for the NIX reader.

Cross-checks ``utils.nix_io`` output for one session against (a) the dataset's
documented structure (NIX_File_Structure.pdf: sampling rates, offsets, channel
labels, trial-property schema, event-onset layout) and (b) an independent re-read of
a single trial's raw DataArray. Per the Dandelion scientific-work standard, this is a
gate: if the expected pattern is not present, the pipeline stops and the discrepancy
is diagnosed before any decoding runs.

Usage:
    .\\venv\\Scripts\\python.exe scripts\\validate_nix_reader.py \\
        --file "D:\\Simultaneous EEG_LFP\\data_nix\\Data_Subject_01_Session_01.h5"

Exit code 0 = all checks pass; 1 = at least one check failed.
"""

from __future__ import annotations

import argparse
import sys

import numpy as np
import nixio

# Allow running as a script from the project root.
sys.path.insert(0, __file__.rsplit("scripts", 1)[0])

from utils import nix_io
from utils.epoching import extract_window, MAINTENANCE_WINDOW_S

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", required=True, help="Path to a Data_Subject_NN_Session_MM.h5 file.")
    ap.add_argument("--rtol", type=float, default=1e-6, help="Relative tolerance for rate/offset checks.")
    args = ap.parse_args()

    checks: list[tuple[str, bool, str]] = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))

    print(f"Validating reader against: {args.file}\n")

    meta = nix_io.read_session_metadata(args.file)
    sub, sess = nix_io.parse_session_filename(args.file)
    check("filename parse", meta.subject_id == sub and meta.session_id == sess,
          f"{meta.subject_id}/{meta.session_id}")

    # --- Acquisition parameters vs documented constants ---
    check("scalp sample rate == 200 Hz",
          np.isclose(meta.scalp_sample_rate_hz, nix_io.EXPECTED_SCALP_RATE_HZ, rtol=args.rtol),
          f"{meta.scalp_sample_rate_hz} Hz")
    check("iEEG sample rate == 2000 Hz",
          np.isclose(meta.ieeg_sample_rate_hz, nix_io.EXPECTED_IEEG_RATE_HZ, rtol=args.rtol),
          f"{meta.ieeg_sample_rate_hz} Hz")
    check("scalp offset == -6 s",
          np.isclose(meta.scalp_offset_s, nix_io.EXPECTED_DATA_OFFSET_S, rtol=args.rtol),
          f"{meta.scalp_offset_s} s")
    check("iEEG offset == -6 s",
          np.isclose(meta.ieeg_offset_s, nix_io.EXPECTED_DATA_OFFSET_S, rtol=args.rtol),
          f"{meta.ieeg_offset_s} s")
    check("scalp channels are known 10-20/mastoid labels",
          len(meta.scalp_channels) > 0
          and set(meta.scalp_channels).issubset(nix_io.EXPECTED_SCALP_LABELS),
          f"{len(meta.scalp_channels)} ch")

    # --- Trial table integrity ---
    n_trials = len(meta.trials)
    check("trials present", n_trials > 0, f"{n_trials} trials")
    set_sizes = sorted({t.set_size for t in meta.trials})
    check("set sizes subset of {4,6,8}", set(set_sizes).issubset({4, 6, 8}), f"{set_sizes}")
    check("load_binary consistent with set_size",
          all((t.load_binary == 0) == (t.set_size == 4) for t in meta.trials))

    # Event-timing invariant the maintenance analysis depends on.
    def all_close(getter, expect):
        vals = [getter(t) for t in meta.trials]
        return all(np.isclose(v, expect, atol=1e-3) for v in vals if not np.isnan(v)), vals
    ok_fix, _ = all_close(lambda t: t.fixation_onset_s, -6.0)
    ok_enc, _ = all_close(lambda t: t.encoding_onset_s, -5.0)
    ok_mnt, _ = all_close(lambda t: t.maintenance_onset_s, -3.0)
    ok_prb, _ = all_close(lambda t: t.probe_onset_s, 0.0)
    check("fixation onset == -6 s (all trials)", ok_fix)
    check("encoding onset == -5 s (all trials)", ok_enc)
    check("maintenance onset == -3 s (all trials)", ok_mnt)
    check("probe onset == 0 s (all trials)", ok_prb)

    # previous_trial_correct == correct shifted by one within session.
    correct_seq = [t.correct for t in meta.trials]
    prev_seq = [t.previous_trial_correct for t in meta.trials]
    ptc_ok = np.isnan(prev_seq[0]) and all(prev_seq[i] == correct_seq[i - 1] for i in range(1, n_trials))
    check("previous_trial_correct aligned", ptc_ok)

    # --- Trial / data-array alignment (independent count) ---
    f = nixio.File.open(args.file, nixio.FileMode.ReadOnly)
    try:
        block = f.blocks[0]
        n_scalp_da = len(block.groups[nix_io.GRP_SCALP].data_arrays)
        n_ieeg_da = len(block.groups[nix_io.GRP_IEEG].data_arrays)
    finally:
        f.close()
    check("metadata trial count == #scalp DataArrays == #iEEG DataArrays",
          n_trials == n_scalp_da == n_ieeg_da,
          f"meta={n_trials}, scalp={n_scalp_da}, ieeg={n_ieeg_da}")

    # --- Scalp epoch loading + windowing ---
    epochs = nix_io.load_scalp_epochs(args.file)
    check("scalp epochs shape matches metadata channels",
          epochs.data.shape[0] == n_trials and epochs.data.shape[1] == len(meta.scalp_channels),
          f"{epochs.data.shape}")
    check("scalp epochs dtype float32", epochs.data.dtype == np.float32, str(epochs.data.dtype))
    check("scalp epochs finite (no NaN/Inf)", np.isfinite(epochs.data).all())

    win = extract_window(epochs.data, epochs.offset_s, epochs.sample_rate_hz, MAINTENANCE_WINDOW_S)
    expected_win_samples = int(round((MAINTENANCE_WINDOW_S[1] - MAINTENANCE_WINDOW_S[0]) * epochs.sample_rate_hz))
    check("maintenance window samples == 3 s * 200 Hz == 600",
          win.shape[-1] == expected_win_samples, f"{win.shape[-1]} samples")

    # --- Independent value cross-check: re-read one trial's raw scalp array ---
    k = min(3, n_trials - 1)
    tnum = int(epochs.trial_ids[k].split("_t")[-1])
    f = nixio.File.open(args.file, nixio.FileMode.ReadOnly)
    try:
        grp = block = f.blocks[0].groups[nix_io.GRP_SCALP]
        target = None
        for da in grp.data_arrays:
            if da.name.endswith(f"Trial_{tnum:02d}"):
                target = np.asarray(da[:], dtype=np.float32)
        independent_ok = target is not None and np.allclose(target, epochs.data[k], atol=1e-4)
    finally:
        f.close()
    check(f"independent re-read of trial {tnum} matches stacked epoch", independent_ok)

    # --- Summary ---
    n_fail = sum(1 for _, ok, _ in checks if not ok)
    print(f"\n{'='*60}")
    print(f"{len(checks) - n_fail}/{len(checks)} checks passed.")
    if n_fail:
        print(f"STOP: {n_fail} check(s) failed. Diagnose before running any decoder.")
        sys.exit(1)
    print("GO: reader output is consistent with the documented dataset structure.")
    sys.exit(0)


if __name__ == "__main__":
    main()
