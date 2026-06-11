# Summary of Only Necessary Context - Codex

**Last rewritten:** 2026-06-11 (Codex Session 3)
**Current phase:** Phase 1 - technical Claim Sheet approved; Accessible Claim Sheet and director review pending

Re-read `AgentPrompt.md`, `Project Details/Project Details.md`, and the active chats at the start of the next session. This file only records Codex-specific continuity not already contained there.

## Current project state

Phase 0 is closed. Claude closed the Phase 0 literature alignment chat and wrote:

- `chats/Claude-Codex/Phase 0 Literature Alignment/Phase 0 Literature Alignment - Concluded.md`
- `chats/Claude-Codex/Phase 0 Literature Alignment/Summary.md`

The technical Claim Sheet is now approved:

- `Claim Sheet.md` is rev. 2 and has Codex approval recorded in `chats/Claude-Codex/Claim Sheet Phase 1/Claim Sheet Phase 1 - Active.md`.
- Codex Session 3 updated the Claim Sheet status header to say the technical sheet is approved.
- Phase 1 is **not closed** yet because the Accessible Claim Sheet and `director_requests.md` entry do not exist.
- Codex Session 3 could not be committed or pushed because `git add` failed with permission denied while creating `.git/index.lock`. The file changes are present in the working tree and need commit/push once `.git` write access is available.

The active Phase 1 chat remains:

- `chats/Claude-Codex/Claim Sheet Phase 1/Claim Sheet Phase 1 - Active.md`

## Technical Claim Sheet approval

Codex approved the technical Claim Sheet in Session 3 after verifying Claude's rev. 2 amendments:

1. **Behavioral-only control label leakage fixed.** Slot 7 excludes set size and any set-size-encoding variable; permitted covariates are response time, correctness, match/mismatch, session, trial order, and timing.
2. **Primary epoch fixed.** Slots 5 and 7 make maintenance-period decoding the headline; encoding and recall are secondary diagnostics.
3. **Concrete success/statistics rule fixed.** Primary target is binary high-vs-low load classification, set size 4 versus 6/8; primary metric is LOSO balanced accuracy during maintenance; success requires at least +0.075 absolute improvement over the strongest non-signal control, at least 7 of 9 held-out subjects above that control, and no single-subject removal dropping mean improvement below +0.04. Evidence must be subject-level; window-level permutation cannot substitute.
4. **Mechanism-layer coverage downgrade fixed.** Phase 2 must audit MTL coverage before mechanism analysis. At least 5 subjects with adequate MTL coverage are required for the mechanism layer to support the full deep-readout claim. If fewer qualify, the project can only claim load decoding with mechanism evidence too sparse or inconclusive.

## Approved labor split

- Claude owns the data layer: NIX reader, event/epoch alignment, LOSO split harness, feature extraction, and primary load-decoding pipeline.
- Codex owns the controls/statistics specification and harness: label-shuffle, behavioral-only with target excluded, timing-only, autocorrelation/window-leakage guard, subject-level permutation/uncertainty, and related reporting.
- Codex leads mechanism-validation analysis once the data layer exposes aligned iEEG/unit inputs.
- Codex owns per-subject verification-dashboard rendering.
- Mechanism validation is co-owned because it depends on Claude's reader/alignment implementation.
- Metrics and the Reproducibility Packet are co-owned.

## Recommended next actions

For Claude's next session:

1. Write `Accessible Claim Sheet.md`.
2. Create `director_requests.md` with the Claim Sheet ready-for-director-review entry.
3. Update any remaining status language and formally close Phase 1 / open Phase 2 once the technical and accessible sheets are aligned.

For Codex's next session:

1. Do not begin Phase 2 implementation unless the Accessible Claim Sheet and director-review entry exist.
2. If Claude has completed Phase 1 closeout, read the technical and accessible sheets for drift, then begin Codex's Phase 2 lane only if the closeout is coherent.
3. If Codex Session 3 changes are still uncommitted, commit/push them before starting new project work.
4. First likely Codex Phase 2 tasks: controls/statistics harness design, subject-level evidence protocol, mechanism coverage audit specification, and dashboard rendering plan, coordinated with Claude's data layer.

## Local substrate facts to carry forward

- Dataset path: `D:\Simultaneous EEG_LFP`
- Local dataset files include 37 session `.h5` files in `data_nix`, MATLAB loading code, README metadata, `datacite.yml`, a CC BY-SA license, and subject/file-structure PDFs.
- Dataset summary from local metadata and paper: 9 epilepsy patients, modified Sternberg verbal working-memory task, simultaneous 10-20 scalp EEG, depth iEEG/LFP, 1526 MTL units, MNI coordinates/anatomical labels, and trial metadata.
- The project virtual environment exists at `.\venv` and uses Python 3.11.9, but currently lacks core dependencies such as NumPy, SciPy, h5py, MNE, scikit-learn, nixio, and torch.
- For all Python work, use only `.\venv\Scripts\python.exe` and `.\venv\Scripts\pip.exe`.

## Codex workspace state

Codex workspace files include:

- `agents/Codex/Literature Foundation.md` - Codex's Phase 0 scientific foundation.
- `agents/Codex/references.md` - Codex's running bibliography.
- `agents/Codex/Phase 1 Claim Sheet Review Scaffold.md` - Codex's technical review checklist.
- `agents/Codex/README.md` - workspace navigation.
- `agents/Codex/Session Summaries/HumanReport1.md`
- `agents/Codex/Session Summaries/HumanReport2.md`
- `agents/Codex/Session Summaries/HumanReport3.md`

## Process reminders

- Codex progress report is due at Session 8 unless a phase transition or approved amendment requires an earlier progress report.
- Active chat files must only be appended to.
- Claude is the default writer for the Claim Sheet, Accessible Claim Sheet, Technical Report, and Accessible Piece. Codex reviews and owns controls/statistics, mechanism-validation analysis, and verification-dashboard rendering once the data layer exists.
- Commit messages should follow `Codex Session <#>`.
