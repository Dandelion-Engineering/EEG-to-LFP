# Summary of Only Necessary Context — Claude

**Last rewritten:** 2026-06-11 (Claude Session 4)
**Current phase:** **Phase 2 — Execution (OPEN).** Data layer built + validated this session. First decoder NOT yet built (gated on one open montage decision with Codex).

> Re-read `/Project Details/Project Details.md` and `AgentPrompt.md` in full at session start — do not duplicate them here. This file only holds what those don't.

## Where the project is right now

- **Phase 0 + Phase 1: CLOSED.** Claim Sheet rev. 2 agent-approved; Accessible Claim Sheet written; both in sync.
- **Phase 2: OPEN.** Session 4 (this one) delivered the entire data layer: deps installed/pinned, NIX reader written + validated (20/20 gate PASS), project-wide trial metadata table built (1827 trials), pre-model trial-count + montage audit run.
- **One decision blocks the first decoder** (see "THE OPEN DECISION" below). Everything else is unblocked.

## What I built this session (all committed except `outputs/`)

- `utils/nix_io.py` — reads each `Data_Subject_NN_Session_MM.h5`. Key entry points:
  - `read_session_metadata(path)` → `SessionMetadata` (per-trial `TrialRecord`s; cheap, no voltages loaded). Use for audits/tables.
  - `load_scalp_epochs(path)` → `ScalpEpochs` (`.data` = (n_trials, n_ch, n_samples) float32 µV, `.channels`, `.sample_rate_hz`, `.offset_s`, `.times_s`).
  - `read_ieeg_electrode_info(path)` → per-contact `{channel, anatomy, mni_xyz}` for the mechanism-coverage audit (lazy).
  - `list_session_files(data_dir)`. Constants: `EXPECTED_SCALP_RATE_HZ=200`, `EXPECTED_IEEG_RATE_HZ=2000`, `EXPECTED_DATA_OFFSET_S=-6`.
- `utils/epoching.py` — `extract_window(data, offset_s, rate, window)`, `MAINTENANCE_WINDOW_S=(-3.0,0.0)`, `time_to_index`.
- `scripts/validate_nix_reader.py` — stop-or-go gate. `--file <h5>`. **20/20 pass on S01/sess01.**
- `scripts/build_trial_metadata.py` — `--data-dir <data_nix> --out-dir outputs`. Writes `trial_metadata.{csv,parquet}` etc.
- `scripts/audit_trial_counts.py` — `--metadata outputs/trial_metadata.csv --montage outputs/scalp_montage.json --out-dir outputs`.
- `requirements.txt` — pinned (numpy 2.4.6, scipy 1.17.1, h5py 3.16.0, nixio 1.5.4, pandas 3.0.3, scikit-learn 1.9.0, matplotlib 3.10.9, pyarrow 24.0.0). All commercial-OK.

**To regenerate outputs:** run `build_trial_metadata.py` then `audit_trial_counts.py` (data-dir = `D:\Simultaneous EEG_LFP\data_nix`). `outputs/` is gitignored but the files persist locally for Codex.

## Verified dataset facts (don't re-derive)

- **37 sessions, 9 subjects, 1827 trials.** One NIX file per session. Block has groups: `Scalp EEG data`, `iEEG data`, `Trial events single tags {scalp/iEEG/spike}`, `Spike times`, `Spike waveforms`, `iEEG electrode information`, `Scalp EEG electrode information`.
- **Scalp 200 Hz, iEEG 2000 Hz, both offset −6 s relative to probe.** Scalp epoch = 1600 samples = [−6, +2] s.
- **Event onsets IDENTICAL across all set sizes & subjects:** fixation −6, encoding −5, **maintenance −3, probe 0** s. Only response time varies with load. ⇒ **maintenance window = fixed [−3, 0] s (600 scalp samples)** with NO timing signature of load → timing-only control should be ~chance. Huge for the claim's credibility.
- **Trial props (numeric, read fine):** Set size (4/6/8), Match, Correct, Response, Response time, Artifact (one per-trial logical — the ONLY quality flag; no separate scalp/iEEG flag), Probe letter (char).
- **nixio quirk:** files use legacy "old values" metadata; nixio decodes char props as strict UTF-8 and crashes on German place-names (General/Task sections). Handled via `_safe_first_value` (latin-1/None fallback). Numeric props unaffected. Don't "fix" by re-reading those char fields — we never use them.
- **iEEG electrode anatomy** present as Sources: e.g. `'Hipp, Left Hippocampus rHipp, rostral hippocampus'` vs `'no_label_found'`. MNI coords in `iEEG_Electrode_MNI_Coordinates`. Unit counts vary 0–139/session; some sessions 0 units (S01 s03/04, S06 s04-07, S07 s01).

## THE OPEN DECISION (blocks the first decoder)

**Scalp montage is NOT uniform across subjects.** Per-subject channel counts: S01/S04/S08 = 19, S05 = 20, S06 = 10, S02/S03/S07/S09 = 8. **Common intersection across all 9 = {F3,F4,C3,C4,O1,O2,A1,A2} = 8 ch (6 brain + A1/A2 ear refs).** LOSO needs a shared feature space ⇒ the headline runs on these 6–8 channels. I posted this to Codex (Phase 2 Controls Interface chat) and **recommended Option 1: keep +0.075, restrict LOSO headline to the 8-channel common montage**, richer-cap subjects' extra channels used only for within-subject diagnostics. Argued against zero/mean-padding (fabricates channels). **Do NOT build the decoder until Codex agrees on the bar+montage.** If he concurs, lock it as the headline config and proceed.

## Trial-count audit result (the Claim-Sheet pre-model gate)

**All 9 subjects PASS — none of Codex's discussion triggers fired. +0.075 stands on the count side.** Per subject, included (non-artifact) low(ss4)/high(ss6,8): S01 61/115, S02 126/193, S03 44/90, S04 36/58, S05 52/81, S06 141/197, S07 66/120, S08 83/132, S09 27/61. Thinnest class = 27 (≥10 ok); ratios 1.40–2.26 (<3:1); artifact 3–14% (<20%). Skew is structural (high pools 2 set sizes) → that's why balanced accuracy is the metric.

## The approved claim (unchanged)

**Slot 3:** scalp EEG holds a subject-transferable, intracranially-validated MTL WM-state signature: LOSO scalp-only predicts WM load above controls (half A) + scalp signature mechanistically tied to MTL theta–alpha coupling that tracks load (half B). **Primary target = WM load binary high(6/8)-vs-low(4), decoded from MAINTENANCE period.** LOSO headline; within-subject diagnostic only. Controls: label-shuffle, behavioral-only (MUST exclude set_size/load_binary — they're the two forbidden columns, named explicitly in `build_trial_metadata.py`), timing-only, subject-identity, artifact. **Success bar:** mean LOSO balanced-acc improvement ≥+0.075 over strongest control, ≥7/9 subjects improvement >0, no single-subject removal drops mean <+0.04; subject-level sign-flip evidence. Mechanism needs ≥5 subjects w/ adequate MTL coverage (coverage audit before mechanism analysis). Model ladder: regularized logistic/LDA → filter-bank covariance+shrinkage → Riemannian → EEGNet → (foundation models optional).

## Next session (my lane), once montage is agreed

1. **Feature extraction** on the common montage: filter-bank band power + covariance over maintenance window. New `utils/features.py` + `scripts/build_features.py` writing the feature bundle Codex specified (`X_signal`, `y`, `groups.{subject,session,trial}_id`, `feature_names`, `feature_family`, `channel_names`, `band_names`, `exclusions`). Decide A1/A2 handling (ear refs — likely re-reference or drop; test both as diagnostic).
2. **LOSO harness** (`make_loso_splits.py` per Codex's naming) + the logistic/LDA baseline rung. Held-out subject scored once; all selection in training subjects; window-level kept on same train/test side (no leakage).
3. Hand the feature bundle + LOSO folds to Codex so his control models run on identical folds.

## Division of labor (ratified)

- **Me (Claude):** data layer ✓ + feature extraction + LOSO harness + primary load-decoding pipeline. Default writer for all 4 narrative docs.
- **Codex:** controls/stats spec ✓ (`agents/Codex/Phase 2 Controls and Statistics Spec.md`) + harness, subject-level uncertainty/permutation, verification-dashboard rendering. Mechanism analysis: Codex leads, co-owned (rides my reader's iEEG/electrode access). Reviewer/approver for my docs.
- **Co-owned:** metrics, Reproducibility Packet. References reconciled jointly.

## Process reminders specific to me

- **Progress reports:** I've written 2 (Phase 0 Close, Phase 1 Close — both phase-transition triggers, neither counts vs the 8-session cadence). Next **cadence** report due at my **Session 8** (this was Session 4). Plus one at each future phase transition / approved amendment.
- **Cross-review (done this session):** read Codex's HumanReport4 + the controls spec it points to + the active chat; my substantive engagement = the spec field-mapping reply + the montage flag. Clean, no pushback needed on his spec — it mapped onto NIX cleanly.
- **Keep Claim Sheet ↔ Accessible Claim Sheet in sync** on any amendment (drift = defect). The montage finding is NOT yet an amendment — it's a Phase 2 config decision pending Codex agreement. If we decide it needs Claim-Sheet language, amend BOTH sheets + write a Progress Report (amendment trigger).
- **Git:** Codex's pushes keep not landing — his Session 4 files were uncommitted in the working tree; I committed them alongside mine (same as Session 3). If `.git/index.lock` errors recur, check it's stale before removing.
- **Session lock:** runs under `.claude-session.lock` (create at start, delete at end). Codex uses `.codex-session.lock`. Scheduled task `dandelion-engineering-4` drives my sessions; AgentPrompt.md workflow.
- **Active chat open:** `chats/Claude-Codex/Phase 2 Controls Interface` — awaiting Codex's montage/bar reply. Conclude it once the decision is settled.
