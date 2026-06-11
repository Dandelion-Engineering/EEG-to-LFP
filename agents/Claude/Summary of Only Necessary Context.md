# Summary of Only Necessary Context — Claude

**Last rewritten:** 2026-06-11 (Claude Session 5)
**Current phase:** **Phase 2 — Execution (OPEN).** Data layer + feature layer + LOSO harness + rung-1 signal model all built and run this session. Montage decision LOCKED. Climbing the model ladder is the next task.

> Re-read `/Project Details/Project Details.md` and `AgentPrompt.md` in full at session start — do not duplicate them here. This file only holds what those don't.

## Where the project is right now

- **Phase 0 + Phase 1: CLOSED.** Claim Sheet rev. 2 agent-approved; Accessible Claim Sheet in sync.
- **Phase 2: OPEN and moving.** Session 4 = data layer. Session 5 (this one) = feature extraction + LOSO folds + rung-1 decoder, run end to end. **First signal result exists.**
- **The montage decision is settled** (was the Session 4 blocker). Codex locked Option 1. No open blockers on my side — next session is pure forward motion on the model ladder.

## What I built this session (Session 5)

- `utils/features.py` — scalp feature extraction. `compute_features(full_epochs, offset_s, fs, channel_names, window_s, bands)` → `FeatureBundle`. Two families: **band_power** (log-variance per ch×band, 5 bands delta/theta/alpha/beta/gamma) and **covariance** (per-band shrunk channel covariance → matrix-log tangent-space vech; Barachant 2012 method). `bandpass_filter` is zero-phase (`sosfiltfilt`) applied to the FULL epoch; the maintenance window is sliced AFTER filtering (no edge-transient leakage). `BANDS`, `COV_SHRINKAGE=0.10`.
- `scripts/build_features.py` — `--data-dir --metadata --montage --out-dir`. Restricts to locked 8-ch montage (fails loudly if a channel is missing — no padding), drops artifact trials (→ `exclusions.csv`), writes `outputs/features/feature_bundle.npz` + sidecars.
- `scripts/make_loso_splits.py` — `--bundle --out-dir`. Writes `loso_folds.json` + `loso_fold_assignment.csv`; validates no subject in train+test, unique trial ids, no empty held-out class.
- `scripts/run_load_decoder.py` — `--bundle --out-dir --model {logistic,lda} --feature-family {band_power,covariance,all} --channel-set {all,brain} --seed`. Rung-1 signal model. Held-out subject touched once (scaler + logistic-C inner subject-grouped CV on train only). Writes `predictions_*`, `subject_scores_*`, `summary_*.json`.

**To regenerate (data-dir = `D:\Simultaneous EEG_LFP\data_nix`):** `build_trial_metadata.py` → `audit_trial_counts.py` → `build_features.py` → `make_loso_splits.py` → `run_load_decoder.py`. All `outputs/` is gitignored but persists locally for Codex.

## The feature bundle contract (what Codex consumes) — `outputs/features/feature_bundle.npz`

- `X_signal` (1683, 220) float32, **scalp-only** (no behavioral/timing cols by construction): band_power (40) + covariance (180). `y` = load_binary. Grouping arrays `subject_id/session_id/trial_id`. Provenance: `feature_names`, `feature_family`, `channel_names`, `channel_role` (A1/A2→reference, rest→brain), `band_names`, `band_low_hz/high_hz`, `window_s`. `cov_matrices` (1683,5,8,8) = shrunk SPD covs for the Riemannian rung.
- Sidecars: `feature_metadata.{parquet,csv}` (per-trial covariates for Codex's behavioral/timing controls), `exclusions.csv` (144 artifact drops), `feature_names.json` (column dictionary). LOSO: `loso_folds.json` + `loso_fold_assignment.csv`.
- **1683 included = 1827 − 144 artifact; low=636 / high=1047. Matches the audit exactly.**

## First signal results (rung 1, signal side only — NOT the final verdict)

Mean LOSO balanced accuracy (chance = 0.50): logistic band_power 8-ch = **0.512**; logistic covariance 8-ch = **0.559**; logistic ALL 8-ch = **0.560** (8/9 subjects > 0.50, headline candidate); LDA all 8-ch = 0.552; **A1/A2-excluded brain-only diagnostic = 0.557** (≈ identical → signal NOT driven by ear refs; Codex's predeclared reference check passes on rung 1). Key finding: spatial covariance carries the signal, band power alone is ~chance — consistent with a distributed (deep-origin) scalp pattern.

**The +0.075 test is signal − strongest_control, computed in CODEX's stats step, not my decoder.** Rung-1 margin may land under +0.075; that's expected headroom for higher ladder rungs, not failure.

## THE LOCKED CONFIG (do not re-litigate)

Codex concurred with Option 1 (chat now concluded). **+0.075 bar stands.** Headline LOSO uses ONLY the common physical montage `{A1,A2,C3,C4,F3,F4,O1,O2}` (8 ch, 6 brain). No padding/imputation/per-subject expansion in the headline. Richer-montage subjects' extra channels = within-subject diagnostics only. Channel roles preserved; brain-only (excl A1/A2) sensitivity diagnostic is predeclared and cannot move the bar after results.

## The approved claim (unchanged)

**Slot 3:** scalp EEG holds a subject-transferable, intracranially-validated MTL WM-state signature. **Primary target = WM load binary high(6/8)-vs-low(4), decoded from MAINTENANCE [−3,0] s.** LOSO headline; within-subject diagnostic only. Controls: label-shuffle, behavioral-only (MUST exclude set_size/load_binary — the two forbidden cols, named in `build_trial_metadata.py`), timing-only, subject-identity, artifact. **Success bar:** mean LOSO balanced-acc improvement ≥+0.075 over strongest control, ≥7/9 subjects improvement >0, no single-subject removal drops mean <+0.04; subject-level sign-flip evidence. Mechanism needs ≥5 subjects w/ adequate MTL coverage (coverage audit before mechanism analysis). Model ladder: **regularized logistic/LDA [DONE — rung 1] → filter-bank covariance+shrinkage → Riemannian → EEGNet → (foundation models optional).**

## Next session (my lane)

1. **Climb the model ladder.** Rung 2 = filter-bank covariance + shrinkage; rung 3 = Riemannian geometry (use `cov_matrices` from the bundle directly — pyriemann if license-OK, else hand-rolled tangent-space + class-mean distance). Goal: see whether signal − strongest_control grows past +0.075. Keep the same LOSO folds and the held-out-once discipline.
2. **Mechanism coverage audit** — which subjects have ≥ adequate MTL electrode coverage (need ≥5). Use `utils.nix_io.read_ieeg_electrode_info(path)` (per-contact anatomy + MNI). This gates the mechanism (half B) analysis, co-owned with Codex.
3. Watch for Codex's control results; once he has them, the +0.075 test can be evaluated on rung 1 and compared as I add rungs.

## Division of labor (ratified)

- **Me (Claude):** data layer ✓ + feature extraction ✓ + LOSO harness ✓ + primary load-decoding pipeline (rung 1 ✓, ladder ongoing). Default writer for all 4 narrative docs.
- **Codex:** controls/stats spec ✓ + harness (label-shuffle, behavioral, timing, subject-identity), subject-level uncertainty/permutation, verification-dashboard rendering. Mechanism: Codex leads, co-owned (rides my reader's iEEG/electrode access). Reviewer/approver for my docs.
- **Co-owned:** metrics, Reproducibility Packet. References reconciled jointly at Phase 2.

## Process reminders specific to me

- **Progress reports:** written 2 (Phase 0 Close, Phase 1 Close — phase-transition triggers, neither counts vs cadence). Next **cadence** report due at my **Session 8** (this was Session 5). Plus one at each future phase transition / approved amendment.
- **Cross-review (done this session):** read Codex's HumanReport5 + his controls spec + the active chat; engaged substantively (consumed his locked config, built to his bundle contract, handed off). No pushback needed.
- **Claim Sheet ↔ Accessible Claim Sheet sync** on any amendment. The montage lock is NOT an amendment — it's a Phase 2 config decision the Claim Sheet already covers (LOSO, balanced acc, +0.075). No amendment / progress report triggered this session.
- **Git:** Codex's pushes keep not landing (his `.git/index.lock` permission error). I committed his Session 5 working-tree files alongside mine (same as Sessions 3–4). If `.git/index.lock` errors recur, check it's stale before removing.
- **Session lock:** `.claude-session.lock` (create at start, delete at end). Codex uses `.codex-session.lock`. Scheduled task `dandelion-engineering-5` drives my sessions; AgentPrompt.md workflow.
- **No active chats open.** Phase 2 Controls Interface is concluded. If Codex's harness needs a bundle change, that opens as a NEW chat.
