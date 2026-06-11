"""Reader for the USZ/NCH "Human MTL units, scalp EEG and iEEG, verbal WM" NIX dataset.

The dataset (G-Node DOI 10.12751/g-node.d76994, CC BY-SA 4.0) stores one NIX/HDF5
file per recording session, named ``Data_Subject_<NN>_Session_<MM>.h5``. Each file
holds, for a modified Sternberg verbal working-memory task:

    * scalp EEG epochs   -- 19 ch, 200 Hz, one DataArray per trial
    * iEEG epochs        -- depth electrodes, 2000 Hz, one DataArray per trial
    * MTL single units   -- spike times / waveforms
    * task metadata       -- per-trial set size, match, correct, response, RT, ...
    * event markers       -- fixation / encoding / maintenance / probe / response onsets
    * electrode metadata  -- MNI coordinates + anatomical labels (iEEG)

This module exposes the dataset to the rest of the pipeline. The headline
load-decoding analysis only needs scalp epochs + task metadata, so those are read
eagerly; iEEG, units, and electrode anatomy (used by the mechanism-validation layer)
are read lazily through separate functions to keep memory bounded on an 8 GB machine.

Implementation notes
--------------------
* The files use NIX's legacy "old values" metadata format. ``nixio`` decodes char
  properties strictly as UTF-8, which crashes on the German place-names in the
  ``General``/``Task`` sections (e.g. "Universitats..."). We never need those fields;
  ``_safe_first_value`` isolates the failure so a single bad char property cannot take
  down a whole-session read.
* Event ``position`` is ``[set_dim_pos, time_pos]``; the onset we want is element 1.
  Onsets are referenced so that probe == 0 s: fixation -6, encoding -5, maintenance -3.
* Data-array sample axis: ``offset`` (s) + index * ``sampling_interval`` (s). Both
  scalp and iEEG arrays start at offset -6 s relative to the probe.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

import numpy as np
import nixio

# ----------------------------------------------------------------------------- #
# Dataset-level constants (verified against NIX_File_Structure.pdf and the files)
# ----------------------------------------------------------------------------- #
EXPECTED_SCALP_RATE_HZ = 200.0          # sampling_interval 0.005 s
EXPECTED_IEEG_RATE_HZ = 2000.0          # sampling_interval 0.0005 s
EXPECTED_DATA_OFFSET_S = -6.0           # both modalities start 6 s before probe
EXPECTED_SCALP_CHANNELS = 19            # 10-20 montage incl. A1/A2

# Event-onset reference (s, probe == 0). Verified constant across set sizes/subjects.
EVENT_NAMES = ("fixation", "encoding", "maintenance", "probe", "response")

# Group names inside each NIX block.
GRP_SCALP = "Scalp EEG data"
GRP_IEEG = "iEEG data"
GRP_EVENTS_SCALP = "Trial events single tags scalp EEG"
GRP_SPIKES = "Spike times"
GRP_IEEG_ELECTRODES = "iEEG electrode information"

_FNAME_RE = re.compile(r"Data_Subject_(\d+)_Session_(\d+)", re.IGNORECASE)
_TRIAL_RE = re.compile(r"Trial_(\d+)")


# ----------------------------------------------------------------------------- #
# Lightweight containers
# ----------------------------------------------------------------------------- #
@dataclass
class TrialRecord:
    """One row of per-trial task metadata (one trial of one session)."""
    subject_id: str
    session_id: str
    trial_id: str
    trial_index: int            # 1-based "Trial number" from the file
    set_size: int               # 4, 6 or 8
    load_binary: int            # 0 for set size 4, 1 for set sizes 6/8
    match: float                # probe match/mismatch code
    correct: int                # 1 correct, 0 incorrect
    response: float             # raw response code
    response_time_s: float
    probe_letter: str
    artifact: bool              # per-trial artifact flag from the dataset
    fixation_onset_s: float
    encoding_onset_s: float
    maintenance_onset_s: float
    probe_onset_s: float
    response_onset_s: float
    previous_trial_correct: float   # correct[t-1] within session; NaN for first trial


@dataclass
class SessionMetadata:
    """Per-session metadata: trial table + acquisition parameters (no signal loaded)."""
    subject_id: str
    session_id: str
    path: str
    trials: list[TrialRecord]
    scalp_channels: list[str]
    n_ieeg_channels: int
    n_units: int
    scalp_sample_rate_hz: float
    ieeg_sample_rate_hz: float
    scalp_offset_s: float
    ieeg_offset_s: float
    n_scalp_samples: int


@dataclass
class ScalpEpochs:
    """Aligned scalp EEG epochs for one session."""
    subject_id: str
    session_id: str
    data: np.ndarray            # (n_trials, n_channels, n_samples), float32, microvolts
    trial_ids: list[str]
    channels: list[str]
    sample_rate_hz: float
    offset_s: float             # time of sample 0 relative to probe
    times_s: np.ndarray = field(repr=False, default=None)  # (n_samples,) sample times


# ----------------------------------------------------------------------------- #
# Helpers
# ----------------------------------------------------------------------------- #
def parse_session_filename(path: str) -> tuple[str, str]:
    """Return (subject_id, session_id) parsed from a Data_Subject_NN_Session_MM filename.

    Raises ValueError if the filename does not match the dataset naming convention,
    so a wrong path fails loudly instead of producing mislabeled records.
    """
    base = os.path.basename(path)
    m = _FNAME_RE.search(base)
    if not m:
        raise ValueError(
            f"Filename '{base}' does not match 'Data_Subject_<NN>_Session_<MM>'. "
            "Pass a file from the dataset's data_nix/ directory."
        )
    return f"S{int(m.group(1)):02d}", f"sess{int(m.group(2)):02d}"


def _safe_first_value(prop):
    """First value of a NIX property, tolerating the dataset's non-UTF8 char fields.

    Returns None if the property cannot be decoded (only happens for char fields we
    do not use). Numeric and ASCII char properties are returned normally.
    """
    try:
        vals = list(prop.values)
    except UnicodeDecodeError:
        return None
    except Exception:
        return None
    return vals[0] if vals else None


def _prop_map(section) -> dict:
    """Map property name -> first value for a NIX metadata section."""
    out = {}
    for p in section.props:
        out[p.name] = _safe_first_value(p)
    return out


def _trial_number(section, fallback_index: int) -> int:
    """Resolve a trial section to its 1-based trial number."""
    pm = _prop_map(section)
    n = pm.get("Trial number")
    if n is not None:
        return int(round(float(n)))
    m = _TRIAL_RE.search(section.name)
    return int(m.group(1)) if m else fallback_index


def _read_event_onsets(block) -> dict[int, dict[str, float]]:
    """Per-trial event onsets (s, probe==0) from the scalp event single-tag group.

    Returns {trial_number: {event_name: onset_s}}. Scalp and iEEG event tags carry
    identical times (per the dataset docs), so reading the scalp group is sufficient.
    """
    grp = block.groups[GRP_EVENTS_SCALP]
    out: dict[int, dict[str, float]] = {}
    for tag in grp.tags:
        name = tag.name
        m = _TRIAL_RE.search(name)
        if not m:
            continue
        trial = int(m.group(1))
        onset = float(list(tag.position)[1])
        slot = out.setdefault(trial, {})
        lname = name.lower()
        if "event_fixation" in lname:
            slot["fixation"] = onset
        elif "event_stimulus" in lname:
            slot["encoding"] = onset
        elif "event_maintenance" in lname:
            slot["maintenance"] = onset
        elif "event_probe" in lname:
            slot["probe"] = onset
        elif "event_response" in lname:
            slot["response"] = onset
    return out


# ----------------------------------------------------------------------------- #
# Metadata reading (cheap: no voltage arrays loaded)
# ----------------------------------------------------------------------------- #
def read_session_metadata(path: str) -> SessionMetadata:
    """Read per-trial task metadata + acquisition parameters for one session file.

    Does NOT load scalp/iEEG voltage arrays (only their shapes and channel labels),
    so this is cheap enough to run across all 37 files for the trial-count audit.

    Args:
        path: absolute path to a Data_Subject_NN_Session_MM.h5 file.

    Returns:
        SessionMetadata with one TrialRecord per trial, ordered by trial number.

    Raises:
        FileNotFoundError, ValueError on malformed input (fails loudly).
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"NIX file not found: {path}")
    subject_id, session_id = parse_session_filename(path)

    f = nixio.File.open(path, nixio.FileMode.ReadOnly)
    try:
        sess_sec = f.sections["Session"]
        trial_props = sess_sec.sections["Trial properties"]
        trial_secs = list(trial_props.sections)
        if not trial_secs:
            raise ValueError(f"{path}: no trial sections under 'Trial properties'.")

        block = f.blocks[0]
        onsets = _read_event_onsets(block)

        # Acquisition parameters from the first scalp + iEEG data arrays.
        scalp_grp = block.groups[GRP_SCALP]
        ieeg_grp = block.groups[GRP_IEEG]
        scalp_da0 = scalp_grp.data_arrays[0]
        ieeg_da0 = ieeg_grp.data_arrays[0]
        scalp_channels = list(scalp_da0.dimensions[0].labels)
        scalp_rate = 1.0 / float(scalp_da0.dimensions[1].sampling_interval)
        ieeg_rate = 1.0 / float(ieeg_da0.dimensions[1].sampling_interval)
        scalp_offset = float(scalp_da0.dimensions[1].offset)
        ieeg_offset = float(ieeg_da0.dimensions[1].offset)
        n_scalp_samples = int(scalp_da0.shape[1])
        n_ieeg_channels = int(ieeg_da0.shape[0])

        # Unit count = number of spike-waveform arrays (one per unit).
        try:
            n_units = len(block.groups["Spike waveforms"].data_arrays)
        except Exception:
            n_units = 0

        # Build ordered trial records.
        raw = []
        for i, sec in enumerate(trial_secs, start=1):
            pm = _prop_map(sec)
            tnum = _trial_number(sec, i)
            ev = onsets.get(tnum, {})
            set_size = int(round(float(pm.get("Set size"))))
            raw.append((tnum, pm, ev, set_size))
        raw.sort(key=lambda r: r[0])

        records: list[TrialRecord] = []
        prev_correct = float("nan")
        for tnum, pm, ev, set_size in raw:
            correct = int(round(float(pm.get("Correct"))))
            probe_letter = pm.get("Probe letter")
            probe_letter = "" if probe_letter is None else str(probe_letter)
            artifact_val = pm.get("Artifact")
            artifact = bool(artifact_val) if artifact_val is not None else False
            rec = TrialRecord(
                subject_id=subject_id,
                session_id=session_id,
                trial_id=f"{subject_id}_{session_id}_t{tnum:03d}",
                trial_index=tnum,
                set_size=set_size,
                load_binary=0 if set_size == 4 else 1,
                match=float(pm.get("Match")) if pm.get("Match") is not None else float("nan"),
                correct=correct,
                response=float(pm.get("Response")) if pm.get("Response") is not None else float("nan"),
                response_time_s=float(pm.get("Response time")) if pm.get("Response time") is not None else float("nan"),
                probe_letter=probe_letter,
                artifact=artifact,
                fixation_onset_s=ev.get("fixation", float("nan")),
                encoding_onset_s=ev.get("encoding", float("nan")),
                maintenance_onset_s=ev.get("maintenance", float("nan")),
                probe_onset_s=ev.get("probe", float("nan")),
                response_onset_s=ev.get("response", float("nan")),
                previous_trial_correct=prev_correct,
            )
            records.append(rec)
            prev_correct = float(correct)

        return SessionMetadata(
            subject_id=subject_id,
            session_id=session_id,
            path=path,
            trials=records,
            scalp_channels=scalp_channels,
            n_ieeg_channels=n_ieeg_channels,
            n_units=n_units,
            scalp_sample_rate_hz=scalp_rate,
            ieeg_sample_rate_hz=ieeg_rate,
            scalp_offset_s=scalp_offset,
            ieeg_offset_s=ieeg_offset,
            n_scalp_samples=n_scalp_samples,
        )
    finally:
        f.close()


# ----------------------------------------------------------------------------- #
# Signal reading (eager scalp epochs; iEEG/units lazy elsewhere)
# ----------------------------------------------------------------------------- #
def load_scalp_epochs(path: str, dtype=np.float32) -> ScalpEpochs:
    """Load aligned scalp EEG epochs for one session.

    Stacks all per-trial scalp DataArrays into a single (n_trials, n_channels,
    n_samples) array. Trials are ordered by trial number to match the metadata table.

    Args:
        path: absolute path to a session .h5 file.
        dtype: output dtype (float32 keeps an all-session load within 8 GB RAM).

    Returns:
        ScalpEpochs with data, trial_ids, channels, sample_rate, offset and times.

    Raises:
        FileNotFoundError, ValueError on malformed input or inconsistent channels.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"NIX file not found: {path}")
    subject_id, session_id = parse_session_filename(path)

    f = nixio.File.open(path, nixio.FileMode.ReadOnly)
    try:
        block = f.blocks[0]
        grp = block.groups[GRP_SCALP]
        # Order arrays by trial number parsed from the array name.
        arrays = []
        for da in grp.data_arrays:
            m = _TRIAL_RE.search(da.name)
            tnum = int(m.group(1)) if m else 0
            arrays.append((tnum, da))
        arrays.sort(key=lambda x: x[0])

        ref_channels = list(arrays[0][1].dimensions[0].labels)
        ref_rate = 1.0 / float(arrays[0][1].dimensions[1].sampling_interval)
        ref_offset = float(arrays[0][1].dimensions[1].offset)
        n_samples = int(arrays[0][1].shape[1])

        data = np.empty((len(arrays), len(ref_channels), n_samples), dtype=dtype)
        trial_ids = []
        for k, (tnum, da) in enumerate(arrays):
            chans = list(da.dimensions[0].labels)
            if chans != ref_channels:
                raise ValueError(
                    f"{path}: trial {tnum} scalp channels differ from trial "
                    f"{arrays[0][0]}; cannot align."
                )
            if int(da.shape[1]) != n_samples:
                raise ValueError(
                    f"{path}: trial {tnum} has {da.shape[1]} samples, expected "
                    f"{n_samples}; cannot stack."
                )
            data[k] = np.asarray(da[:], dtype=dtype)
            trial_ids.append(f"{subject_id}_{session_id}_t{tnum:03d}")

        times = ref_offset + np.arange(n_samples) / ref_rate
        return ScalpEpochs(
            subject_id=subject_id,
            session_id=session_id,
            data=data,
            trial_ids=trial_ids,
            channels=ref_channels,
            sample_rate_hz=ref_rate,
            offset_s=ref_offset,
            times_s=times,
        )
    finally:
        f.close()


def read_ieeg_electrode_info(path: str) -> list[dict]:
    """Read iEEG electrode anatomy + MNI coordinates for the mechanism-coverage audit.

    Returns one dict per iEEG contact with keys: ``channel`` (electrode label),
    ``anatomy`` (anatomical-location source name, e.g. 'Hipp, Left Hippocampus ...'
    or 'no_label_found'), and ``mni_xyz`` (list of 3 floats or None).

    This is read lazily (separate from the headline scalp pipeline) because only the
    mechanism-validation layer needs it.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"NIX file not found: {path}")
    f = nixio.File.open(path, nixio.FileMode.ReadOnly)
    try:
        block = f.blocks[0]
        grp = block.groups[GRP_IEEG_ELECTRODES]
        mni = None
        for da in grp.data_arrays:
            if "MNI" in da.name:
                mni = np.asarray(da[:])
        out = []
        for i, src in enumerate(grp.sources):
            subs = list(src.sources)
            channel = subs[0].name if len(subs) >= 1 else src.name
            anatomy = subs[1].name if len(subs) >= 2 else "unknown"
            xyz = None
            if mni is not None and i < mni.shape[0]:
                xyz = [float(v) for v in mni[i]]
            out.append({"channel": channel, "anatomy": anatomy, "mni_xyz": xyz})
        return out
    finally:
        f.close()


def list_session_files(data_dir: str) -> list[str]:
    """Return sorted absolute paths of all Data_Subject_*_Session_*.h5 files in data_dir."""
    if not os.path.isdir(data_dir):
        raise NotADirectoryError(f"data_nix directory not found: {data_dir}")
    files = [
        os.path.join(data_dir, fn)
        for fn in os.listdir(data_dir)
        if _FNAME_RE.search(fn) and fn.lower().endswith(".h5")
    ]
    if not files:
        raise FileNotFoundError(f"No Data_Subject_*_Session_*.h5 files found in {data_dir}")
    return sorted(files)
