# Summary of Only Necessary Context - Codex

**Last rewritten:** 2026-06-11 (Codex Session 4)
**Current phase:** Phase 2 - Execution open

Re-read `AgentPrompt.md`, `Project Details/Project Details.md`, the Claim Sheet pair, and active chats at the start of the next session. This file only records Codex-specific continuity not already contained there.

## Current project state

Phase 0 and Phase 1 are closed.

- Phase 0 Literature Alignment is concluded:
  - `chats/Claude-Codex/Phase 0 Literature Alignment/Phase 0 Literature Alignment - Concluded.md`
  - `chats/Claude-Codex/Phase 0 Literature Alignment/Summary.md`
- Phase 1 Claim Sheet Review is concluded:
  - `chats/Claude-Codex/Claim Sheet Phase 1/Claim Sheet Phase 1 - Concluded.md`
  - `chats/Claude-Codex/Claim Sheet Phase 1/Summary.md`
- `Claim Sheet.md` is agent-approved rev. 2 and says Phase 1 is closed / Phase 2 is open.
- `Accessible Claim Sheet.md` exists and is the director-facing companion to the technical Claim Sheet.
- `director_requests.md` exists. Request 1 asks Randy to review the Claim Sheet pair. This is non-blocking; Phase 2 proceeds while waiting.
- Git history currently has `94312f5 Claude Session 3` at `HEAD` and `origin/main`; Claude committed Codex Session 3's uncommitted closeout files along with the Phase 1 closeout.

No Phase 2 analysis code exists yet. No pinned `requirements.txt`, NIX reader, aligned epoch output, feature extraction, controls harness, or dashboard renderer exists yet.

## Codex Session 4 work

Codex Session 4 did not implement model code because Claude's data layer does not exist and the Claim Sheet requires a trial-count audit before any decoder result is observed.

Codex created:

- `agents/Codex/Phase 2 Controls and Statistics Spec.md`
- `chats/Claude-Codex/Phase 2 Controls Interface/Phase 2 Controls Interface - Active.md`
- `agents/Codex/Session Summaries/HumanReport4.md`

The controls/statistics spec defines what Codex will need from Claude's reader/aligned-epoch layer: trial metadata, epoch/window metadata, feature bundle shape, control definitions, trial-count audit outputs, subject-level evidence rules, and verification-dashboard prediction-table inputs. It emphasizes explicit validation of forbidden behavioral-control inputs and leakage guards.

The new active chat asks Claude to preserve those data-layer semantics while building the NIX reader. It specifically flags `previous_trial_correct` as useful because the dataset paper states an incorrect trial is always followed by a set-size-4 trial, which could create a trial-order confound.

## Approved labor split

- Claude owns the data layer: pinned dependency install, NIX reader, event/epoch alignment, LOSO split harness, feature extraction, and primary load-decoding pipeline.
- Codex owns the controls/statistics specification and harness: label-shuffle, behavioral-only with target excluded, timing-only, autocorrelation/window-leakage guard, subject-level permutation/uncertainty, and related reporting.
- Codex leads verification-dashboard per-subject rendering.
- Mechanism validation is co-owned. Codex leads analysis, but it depends on Claude's reader/alignment exposing iEEG/unit inputs and MTL coverage metadata.
- Metrics and the Reproducibility Packet are co-owned.

## Next actions

For Claude's next session:

1. Read the active `Phase 2 Controls Interface` chat and Codex's spec before finalizing reader output shapes.
2. Install pinned dependencies into `venv` using only `.\venv\Scripts\python.exe` / `.\venv\Scripts\pip.exe`.
3. Create `requirements.txt` with pinned versions and document dependency licenses.
4. Build the NIX reader and validate it against the dataset's MATLAB loader / `NIX_File_Structure.pdf` before trusting outputs.
5. Produce the pre-model trial-count audit: maintenance-period trials by subject/session/set size, rejected trials, binary high/low counts, and class imbalance.
6. If the counts challenge the +0.075 success bar, open a Claude-Codex discussion before any model runs.

For Codex's next session:

1. First check whether Claude has responded in `chats/Claude-Codex/Phase 2 Controls Interface/Phase 2 Controls Interface - Active.md`.
2. If the data layer and trial-count audit still do not exist, do not implement model-scoring code. Continue only with interface/specification or dashboard design work that does not observe model results.
3. If aligned epoch outputs and the trial-count audit exist, review them for control compatibility, leakage risks, and whether the success bar remains fair before implementing the controls harness.
4. Implement controls only after the pre-model audit is complete and any bar discussion is resolved.

## Hard technical guards to preserve

- Primary target: binary high-vs-low load, set size 4 vs set sizes 6/8.
- Headline epoch: maintenance period.
- Headline split: leave-one-subject-out.
- Held-out subject is scored once; all model/feature/window choices happen inside training subjects only.
- Adjacent windows from the same trial cannot straddle train/test boundaries.
- Behavioral-only control must exclude set size and every set-size-encoding variable.
- Evidence is subject-level. Window-level permutation cannot substitute.
- Success bar remains the Claim Sheet bar unless changed before modeling: mean balanced-accuracy improvement >= 0.075 over strongest non-signal control, at least 7/9 subjects above control, and no single-subject removal dropping mean improvement below 0.04.
- Mechanism full-claim support requires at least 5 subjects with adequate MTL coverage. Fewer than 5 means the mechanism layer is too sparse for the full deep-readout claim.

## Local substrate facts

- Dataset path: `D:\Simultaneous EEG_LFP`
- Local dataset files are expected to include 37 session `.h5` files in `data_nix`, MATLAB loading code, README metadata, `datacite.yml`, a CC BY-SA license, and subject/file-structure PDFs.
- Dataset summary: 9 epilepsy patients, modified Sternberg verbal working-memory task, simultaneous 10-20 scalp EEG, depth iEEG/LFP, 1526 MTL units, MNI coordinates/anatomical labels, and trial metadata.
- The task has encoding, 3-second maintenance, and recall/probe periods. The dataset paper says an incorrect trial is always followed by a set-size-4 trial; controls should audit this possible trial-order confound.
- Scalp EEG is resampled to 200 Hz; iEEG is resampled to 2 kHz.
- The project virtual environment exists at `.\venv` and uses Python 3.11.9, but currently lacks the Phase 2 dependency stack.
- For all Python work, use only `.\venv\Scripts\python.exe` and `.\venv\Scripts\pip.exe`.

## Codex workspace state

Codex workspace files include:

- `agents/Codex/Literature Foundation.md`
- `agents/Codex/references.md`
- `agents/Codex/Phase 1 Claim Sheet Review Scaffold.md`
- `agents/Codex/Phase 2 Controls and Statistics Spec.md`
- `agents/Codex/README.md`
- `agents/Codex/Summary of Only Necessary Context.md`
- `agents/Codex/Session Summaries/HumanReport1.md`
- `agents/Codex/Session Summaries/HumanReport2.md`
- `agents/Codex/Session Summaries/HumanReport3.md`
- `agents/Codex/Session Summaries/HumanReport4.md`

## Process reminders

- Codex progress report is due at Session 8 unless a phase transition or approved amendment requires an earlier progress report.
- Active chat files must only be appended to.
- Claude is the default writer for the Claim Sheet, Accessible Claim Sheet, Technical Report, and Accessible Piece. Codex reviews and owns controls/statistics, mechanism-validation analysis, and verification-dashboard rendering once the data layer exists.
- Commit messages should follow `Codex Session <#>`.
