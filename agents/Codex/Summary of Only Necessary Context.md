# Summary of Only Necessary Context - Codex

**Last rewritten:** 2026-06-12 18:19 PDT (Codex Session 14)
**Current phase:** Phase 3 deliverables approved/closeable after Amendment 1

Re-read `AgentPrompt.md`, `Project Details/Project Details.md`, the dataset paper in `Project Details/`, the Claim Sheet pair, and Codex-related chat summaries at the start of the next session. This file records Codex-specific continuity not already contained there.

## Current Project State

Phase 0 and Phase 1 are closed. Randy approved the original Claim Sheet pair in the concluded `chats/Claude-Codex-Human/Some Updates/` thread with no director amendments.

Amendment 1 is ratified in both `Claim Sheet.md` and `Accessible Claim Sheet.md`. It records the completed model ladder as a bounded negative and the EEGNet-to-MTL coupling as an exploratory/inconclusive mechanism lead. The original Slot 11 decoding success bar was not weakened.

All Codex-including chats are concluded at this closeout. The newest concluded chat is:

- `chats/Claude-Codex/Reproducibility Packet Review/Reproducibility Packet Review - Concluded.md`
- `chats/Claude-Codex/Reproducibility Packet Review/Summary.md`

Phase 3 is closeable from Codex's side. The Accessible Piece is approved, the Technical Report source is approved, and the Reproducibility Packet is approved after clean-output validation.

## Locked Original Headline Configuration

The original locked Phase 2 headline configuration defines the clean negative result:

- primary target: binary high-vs-low load, set size 4 vs set sizes 6/8;
- headline epoch: maintenance period `[-3, 0]` seconds relative to probe;
- headline split: leave-one-subject-out;
- headline scalp montage: the 8 common physical channels `A1`, `A2`, `C3`, `C4`, `F3`, `F4`, `O1`, `O2`;
- no missing-channel padding, imputation, or subject-specific expanded feature spaces for the headline;
- success bar: mean LOSO balanced-accuracy improvement over strongest non-signal control at least `+0.075`, at least `7/9` held-out subjects above control, and no leave-one-subject-removed mean below `0.04`;
- evidence is subject-level; window-level permutation cannot substitute.

Do not run additional headline decoders to rescue this bar. Frequency-domain CNNs, richer channel sets, or within-subject runs would be diagnostics/new claims, not a rescue of the locked common-montage LOSO headline.

## Completed Decoding Results

The pre-registered model ladder is exhausted:

- `logistic_all_all`: mean signal BA `0.560`; strongest-control BA `0.593`; improvement `-0.033`; `3/9` subjects above control; headline success `no`.
- `tangent_cov_all`: mean signal BA `0.558`; strongest-control BA `0.593`; improvement `-0.036`; `3/9` subjects above control; headline success `no`.
- `eegnet_raw_all`: mean signal BA `0.616`; strongest-control BA `0.593`; improvement `+0.023`; `5/9` subjects above control; min leave-one-subject-removed mean `-0.001`; bootstrap 95% CI `[-0.022, 0.081]`; headline success `no`.

EEGNet was the first rung to beat behavioral control on the mean, but it fails the declared bar and is S04-driven:

```text
S01 improvement  +0.045
S02 improvement  -0.055
S03 improvement  -0.015
S04 improvement  +0.218
S05 improvement  -0.067
S06 improvement  +0.045
S07 improvement  -0.015
S08 improvement  +0.009
S09 improvement  +0.044
```

Removing S04 drops mean improvement to `-0.001`. Treat this as the clean negative boundary the robustness rule was designed to catch.

The brain-only EEGNet diagnostic remains: mean LOSO BA `0.623` on the 6 brain channels vs `0.616` on all 8 channels. This passes the A1/A2 reference sensitivity check for rung 4 and does not change the headline failure.

## Behavioral-Control State

The strongest non-signal control remains behavioral-only for all subjects. Codex Session 7 showed that it is almost entirely `previous_trial_correct`, reflecting the task rule that an incorrect response is followed by a set-size-4 trial:

```text
previous_trial_correct = 0.0: current high-load rate 0.015
previous_trial_correct = 1.0: current high-load rate 0.670
previous_trial_correct = missing: current high-load rate 0.800
```

This is not response-time leakage, correctness/match leakage, or session/trial-order drift. It was predeclared as an allowed behavioral covariate, so it remains the valid strongest control under the current Claim Sheet.

## Mechanism State

MTL coverage is adequate for all `9/9` subjects. Coverage alone does not support the deep-readout claim.

The MTL band-power probe against EEGNet scores found a real MTL theta-alpha substrate and a suggestive raw coupling:

```text
MTL theta-alpha load effect z: mean 0.143, 7/9 positive, p2=0.0156
corr(EEGNet score, MTL theta): mean 0.078, 6/9 positive, p2=0.1641
corr(EEGNet score, MTL alpha): mean 0.057, 6/9 positive, p2=0.2852
corr(EEGNet score, theta-alpha): mean 0.068, 7/9 positive, p2=0.0508
```

Codex Session 11 added and ran `scripts/run_mtl_confirmatory_coupling_gate.py` as the prospective Part B gate. Gate criteria:

- fixed metric: `corr_schedule_residual_score_mtl_theta_alpha_diff`;
- mean correlation must be positive;
- at least `7/9` subjects positive;
- exact two-sided subject sign-flip `p <= 0.05`;
- every leave-one-subject-out mean must be above `0`.

Result:

```text
gate_passed = False
schedule-residualized mean = 0.011
positive subjects = 4/9
p2 = 0.7461
min leave-one-subject-out mean = -0.010
```

Interpretation: Part B remains exploratory/inconclusive. Do not describe the raw coupling as validated deep-source-related information.

## Deliverable State After Session 14

Accessible Piece: approved by Codex Session 12 after one precision edit.

Technical Report: source approved by Codex Session 13. `deliverables/technical_report/main.tex` and `README.md` say source approved. Report source checks passed: no missing citation keys, no missing figure paths, and relevant report/dashboard scripts compile. Local PDF verification remains blocked by MiKTeX before source processing: `pdflatex` cannot rebuild `pdflatex.fmt` because `formats.ini` is missing and the local MiKTeX lock path has a permission failure.

Reproducibility Packet: approved by Codex Session 14. `deliverables/reproducibility_packet/` remains a repository-as-reproduction-unit packet; `scripts/` and `utils/` are not duplicated into the packet.

The strict clean-output validation gate is closed. Claude Session 12 recorded a full clean-room end-to-end reproduction in `outputs_cleanroom/` while Codex sessions overlapped; Claude Session 13 pointed Codex back to that completed branch-(a) validation and approved the packet as co-owner. Codex Session 14 then gave the final explicit packet stamp and independently completed a scratch-tree confirmation:

- default clean-output EEGNet run finished in `scratch/repro_validation_20260612_133941/outputs/` after about 98 minutes;
- clean EEGNet reproduced mean signal BA `0.616`;
- downstream controls/statistics/mechanism/dashboard were regenerated from the same clean tree;
- regenerated dashboard was byte-identical to `deliverables/reproducibility_packet/verification_dashboard.html`;
- regenerated statistics summary was byte-identical to canonical `outputs/statistics/summary_eegnet_raw_all.json`;
- regenerated confirmatory-gate JSON differed only by recorded scratch-tree input paths, with matching observed values and failed verdict.

Codex Session 14 wrote `agents/Codex/Progress Reports/Progress Report Phase 3 Close.md`.

## Files Changed In Session 14

- `chats/Claude-Codex/Reproducibility Packet Review/Reproducibility Packet Review - Concluded.md` - final packet approval appended and transcript concluded.
- `chats/Claude-Codex/Reproducibility Packet Review/Summary.md` - summary of the concluded packet review.
- `agents/Codex/Progress Reports/Progress Report Phase 3 Close.md` - director-facing Phase 3 close report.
- `agents/Codex/Session Summaries/HumanReport14.md` - Session 14 report.
- `agents/Codex/README.md` - refreshed navigation and Phase 3 close state.
- `agents/Codex/Summary of Only Necessary Context.md` - this file.

Generated/ignored artifacts from validation:

- `scratch/repro_validation_20260612_133941/outputs/decoding/predictions_eegnet_raw_all.csv`
- `scratch/repro_validation_20260612_133941/outputs/decoding/subject_scores_eegnet_raw_all.csv`
- downstream ignored clean-output artifacts under `scratch/repro_validation_20260612_133941/outputs/{controls,statistics,mechanism,amendment,dashboard}/`

## Git Closeout State

Codex Session 14 attempted the required stage/commit/push after all closeout files were written. The attempt failed before staging:

```text
fatal: Unable to create '.../.git/index.lock': Permission denied
```

`Test-Path .git\index.lock` returned `False`, so this is not a stale lock file. A direct write test inside `.git` also hit access denied. The Session 14 files remain uncommitted and unpushed in the working tree. A future run with Git metadata write access should stage and commit them as `Codex Session 14`, or Claude/Randy may include the completed Codex session work in a later combined commit under the agreed protocol.

## Next Steps

1. Commit and push the uncommitted Session 14 files if Git metadata write access is available.
2. Do not reopen the model ladder or soften the bounded-negative wording.
3. If the project needs a final compiled PDF, repair or replace MiKTeX first; source approval is already complete.
4. Future work should be treated as a new claim/future project unless Randy explicitly asks for maintenance on the existing deliverables.

## Hard Guards To Preserve

- Held-out subject is scored once; all model/feature/window choices happen inside training subjects only.
- Adjacent windows from the same trial cannot straddle train/test boundaries.
- Behavioral-only control must exclude set size, `load_binary`, and every set-size-encoding variable.
- Timing-only control must not include response time, correctness, match/mismatch, neural features, or target encodings.
- A1/A2 are ear/mastoid references; brain-only diagnostics are required but cannot move the headline bar after results are observed.
- Mechanism full-claim support requires adequate MTL coverage and actual coupling evidence, not coverage alone.
- Raw EEGNet-to-MTL coupling `p2=0.0508` is exploratory because the residualized confirmatory gate failed.
- No raw dataset files, large binaries, generated ignored outputs, scratch probes, local lock files, or local venv files should be committed.

## Local Substrate Facts

- Dataset path: `D:\Simultaneous EEG_LFP`.
- Dataset NIX directory: `D:\Simultaneous EEG_LFP\data_nix` (37 `Data_Subject_*.h5` files).
- Project virtual environment exists at `.\venv`; always use `.\venv\Scripts\python.exe` and `.\venv\Scripts\pip.exe`.
- Common maintenance timing is fixed across trials: fixation `-6 s`, encoding `-5 s`, maintenance `-3 s`, probe `0 s`.
- iEEG data arrays are trial-aligned, typically shaped `(n_contacts, 16000)`, sampled at `2000 Hz`, and offset `-6 s` relative to probe.
