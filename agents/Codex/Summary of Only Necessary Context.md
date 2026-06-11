# Summary of Only Necessary Context - Codex

**Last rewritten:** 2026-06-11 (Codex Session 5)
**Current phase:** Phase 2 - Execution open

Re-read `AgentPrompt.md`, `Project Details/Project Details.md`, the Claim Sheet pair, and active chats at the start of the next session. This file only records Codex-specific continuity not already contained there.

## Current project state

Phase 0 and Phase 1 are closed. The technical Claim Sheet is agent-approved rev. 2, `Accessible Claim Sheet.md` exists, and `director_requests.md` still has Request 1 asking Randy to review the Claim Sheet pair. That request is non-blocking.

Phase 2 is open. Claude owns the data layer and primary load-decoding pipeline. Codex owns controls/statistics, subject-level evidence, and the verification-dashboard rendering lane. Mechanism validation is co-owned, with Codex leading analysis once iEEG/unit inputs are exposed through Claude's reader.

## Data layer and audit status

Claude Session 4 built the initial data layer and committed it:

- `utils/nix_io.py`
- `utils/epoching.py`
- `scripts/validate_nix_reader.py`
- `scripts/build_trial_metadata.py`
- `scripts/audit_trial_counts.py`
- pinned `requirements.txt`

Claude also generated local rebuildable outputs under `outputs/`:

- `trial_metadata.csv` / `.parquet` with 1827 trial rows across 9 subjects and 37 sessions
- `trial_count_audit.md` / `.csv`
- `trial_count_by_setsize.csv`
- `scalp_montage.json`
- `montage_intersection.json`
- `session_summary.csv`

The trial-count audit passed the pre-model gate:

- no empty classes;
- no subject with fewer than 10 trials in either binary class;
- no high/low class ratio above 3:1;
- no artifact exclusion fraction above 20%;
- smallest class is S09 low-load with 27 included trials.

The predeclared success bar remains unchanged: mean LOSO balanced-accuracy improvement >= 0.075 above strongest non-signal control, at least 7/9 held-out subjects above control, and no single-subject removal dropping mean improvement below 0.04.

No decoder/model result has been run or observed as of Codex Session 5.

## Git closeout status

Codex Session 5 could not commit or push. `git add` failed with:

```text
fatal: Unable to create '.../.git/index.lock': Permission denied
```

There was no existing `.git/index.lock`, so this appears to be a repository-metadata write restriction in the current sandbox. The project files are updated in the working tree but remain uncommitted. A future session with Git metadata write access should stage the Session 5 changes and commit them as `Codex Session 5` before adding further work if possible.

## Locked montage decision from Codex Session 5

Claude's audit found the scalp montage is not uniform across subjects:

- S01/S04/S08: 19 channels
- S05: 20 channels
- S06: 10 channels
- S02/S03/S07/S09: 8 channels
- common intersection across all 9 subjects: `A1`, `A2`, `C3`, `C4`, `F3`, `F4`, `O1`, `O2`
- common brain-channel subset excluding ear/mastoid references: `C3`, `C4`, `F3`, `F4`, `O1`, `O2`

Codex Session 5 responded in `chats/Claude-Codex/Phase 2 Controls Interface/Phase 2 Controls Interface - Active.md` and locked the headline configuration:

- keep the +0.075 success bar;
- use only the 8-channel common physical montage for the headline LOSO signal features;
- forbid missing-channel padding, imputation, or subject-specific expanded feature spaces for the headline result;
- allow richer subject montages only for within-subject or other explicitly labeled diagnostics;
- preserve channel-role metadata;
- include a predeclared artifact/reference sensitivity diagnostic on the 6 common brain channels excluding `A1`/`A2`.

The 6-channel sensitivity diagnostic cannot replace the locked headline result or move the success bar after results are observed. If a headline result is dominated by `A1`/`A2`, it must be discussed as a reference/artifact risk.

This decision is also recorded in `agents/Codex/Phase 2 Controls and Statistics Spec.md`.

## Validation fix from Codex Session 5

Codex noticed that `scripts/validate_nix_reader.py` still asserted 19 scalp channels as a dataset-wide invariant, which conflicted with Claude's montage audit. Codex patched:

- `utils/nix_io.py`: replaced the fixed expected scalp-channel count with the observed valid 10-20/mastoid label set.
- `scripts/validate_nix_reader.py`: validates known labels and epoch shape matching per-session metadata rather than a fixed 19-channel shape.
- `scripts/build_trial_metadata.py`: corrected the montage sidecar comment to say it records whether labels are constant across sessions.

Verification run in Codex Session 5:

- `.\venv\Scripts\python.exe -m py_compile scripts\validate_nix_reader.py scripts\build_trial_metadata.py scripts\audit_trial_counts.py utils\nix_io.py utils\epoching.py`
- `.\venv\Scripts\python.exe scripts\validate_nix_reader.py --file "D:\Simultaneous EEG_LFP\data_nix\Data_Subject_01_Session_01.h5"` -> 20/20 checks passed, 19 channels.
- `.\venv\Scripts\python.exe scripts\validate_nix_reader.py --file "D:\Simultaneous EEG_LFP\data_nix\Data_Subject_02_Session_01.h5"` -> 20/20 checks passed, 8 channels.
- `git diff --check` passed with only normal CRLF warnings.

## Active chat state

Active chat:

- `chats/Claude-Codex/Phase 2 Controls Interface/Phase 2 Controls Interface - Active.md`

Latest Codex message tells Claude he is clear to proceed to common-montage feature extraction under the locked configuration. No Codex response is currently pending unless Claude adds a new question.

Concluded chats:

- `chats/Claude-Codex/Phase 0 Literature Alignment/`
- `chats/Claude-Codex/Claim Sheet Phase 1/`

## Hard guards to preserve

- Primary target: binary high-vs-low load, set size 4 vs set sizes 6/8.
- Headline epoch: maintenance period `[-3, 0]` seconds relative to probe.
- Headline split: leave-one-subject-out.
- Held-out subject is scored once; all model/feature/window choices happen inside training subjects only.
- Adjacent windows from the same trial cannot straddle train/test boundaries.
- Behavioral-only control must exclude set size, `load_binary`, and every set-size-encoding variable.
- Timing-only control must not include response time, correctness, match/mismatch, neural features, or target encodings.
- Evidence is subject-level. Window-level permutation cannot substitute.
- Mechanism full-claim support requires at least 5 subjects with adequate MTL coverage. Fewer than 5 means the mechanism layer is too sparse for the full deep-readout claim.
- No raw dataset files, large binaries, generated outputs, scratch probes, or local venv files should be committed.

## Next actions

For Claude's next session:

1. Proceed to feature extraction on the locked common 8-channel physical montage.
2. Preserve channel-role metadata and stable feature names with channel, band, statistic, and window encoded.
3. Keep richer-montage features out of the headline LOSO run.
4. Do not fit decoders using padded/imputed channels.

For Codex's next session:

1. First check the active `Phase 2 Controls Interface` chat for Claude's response or feature-output handoff.
2. If feature bundles and LOSO fold definitions exist, review them for the locked montage, forbidden control inputs, leakage risks, and stable join keys.
3. Implement the controls harness only after the feature-output contract is concrete.
4. Controls to implement: label-shuffle, behavioral-only, timing-only, forbidden-input hard failures, subject-level improvement/statistics, and dashboard input validation.
5. Keep the `A1`/`A2` sensitivity diagnostic predeclared and separate from the headline success criteria.

## Local substrate facts

- Dataset path: `D:\Simultaneous EEG_LFP`
- Dataset files include 37 session `.h5` files in `data_nix`, MATLAB loading code, README metadata, `datacite.yml`, CC BY-SA license, and subject/file-structure PDFs.
- Project virtual environment exists at `.\venv`; always use `.\venv\Scripts\python.exe` and `.\venv\Scripts\pip.exe`.
- Common maintenance timing is fixed across trials: fixation -6 s, encoding -5 s, maintenance -3 s, probe 0 s.
