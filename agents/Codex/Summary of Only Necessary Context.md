# Summary of Only Necessary Context - Codex

**Last rewritten:** 2026-06-11 16:43 PDT (Codex Session 8)
**Current phase:** Phase 2 execution open

Re-read `AgentPrompt.md`, `Project Details/Project Details.md`, the Claim Sheet pair, and Codex-related chat summaries at the start of the next session. This file records only Codex-specific continuity not already contained there.

## Current Project State

Phase 0 and Phase 1 are closed. The technical `Claim Sheet.md` is agent-approved rev. 2, `Accessible Claim Sheet.md` exists, and `director_requests.md` still has Request 1 asking Randy to review the Claim Sheet pair. That request is non-blocking.

Phase 2 remains open. The locked headline configuration and success bar have not changed:

- primary target: binary high-vs-low load, set size 4 vs set sizes 6/8;
- headline epoch: maintenance period `[-3, 0]` seconds relative to probe;
- headline split: leave-one-subject-out;
- headline scalp montage: the 8 common physical channels `A1`, `A2`, `C3`, `C4`, `F3`, `F4`, `O1`, `O2`;
- no missing-channel padding, imputation, or subject-specific expanded feature spaces for the headline;
- success bar: mean LOSO balanced-accuracy improvement over strongest non-signal control at least `+0.075`, at least `7/9` held-out subjects above control, and no leave-one-subject-removed mean below `0.04`;
- evidence is subject-level; window-level permutation cannot substitute.

## Available Local Artifacts

Generated outputs remain intentionally ignored by git under `/outputs/`, but the local workspace has:

- `outputs/features/feature_bundle.npz` with the scalp signal matrix, labels, subject/session/trial IDs, feature names/families, channel roles, and covariance matrices;
- `outputs/features/feature_metadata.csv` and `.parquet`;
- `outputs/features/loso_folds.json` and `loso_fold_assignment.csv`;
- signal-model outputs under `outputs/decoding/` for logistic, LDA, Riemannian tangent/MDM, and brain-only diagnostics;
- controls/statistics outputs for `logistic_all_all` and `tangent_cov_all`;
- MTL coverage audit outputs under `outputs/mechanism/`;
- behavioral-control ablation outputs under `outputs/controls/behavioral_ablation_*`;
- first MTL band-power mechanism probe outputs under `outputs/mechanism/mtl_bandpower_*_tangent_cov_all.*`.

There are no completed EEGNet prediction/subject-score outputs yet (`outputs/decoding/predictions_eegnet_*` absent as of Session 8). `scripts/run_eegnet_decoder.py` and `utils/eegnet.py` were already untracked at Session 8 startup; Codex Session 8 read them but did not run, edit, stage, or claim them.

## Decoding Results So Far

First controlled rung, `logistic_all_all`:

- mean signal balanced accuracy: `0.560`;
- mean strongest-control balanced accuracy: `0.593`;
- mean improvement: `-0.033`;
- subjects above strongest control: `3/9`;
- headline success: `no`;
- strongest control: behavioral-only for all `9/9` subjects.

Claude Session 6 climbed the linear-to-Riemannian ladder. Best completed new rung, `tangent_cov_all`:

- mean signal balanced accuracy: `0.558`;
- mean strongest-control balanced accuracy: `0.593`;
- mean improvement: `-0.036`;
- subjects above strongest control: `3/9`;
- headline success: `no`;
- brain-only tangent diagnostic around `0.556`, so the weak signal is not driven by A1/A2 references.

Interpretation: logistic/LDA/Riemannian rungs do not beat the strongest allowed non-signal control. The model-class plateau is probably the 8-channel common montage plus cross-subject transfer, not insufficient covariance geometry. EEGNet is still pending.

## Behavioral-Control Ablation

Codex Session 7 added `scripts/run_behavioral_control_ablation.py` and ran it against the current feature bundle/metadata.

Mean LOSO balanced accuracy:

```text
rt_only              0.500
correct_match        0.500
previous_trial       0.596
trial_index_only     0.500
session_only         0.500
trial_order_session  0.500
full_behavioral      0.593
```

`previous_trial_correct` was the best ablation for all `9/9` held-out subjects. The target-rate audit explains the control:

```text
previous_trial_correct = 0.0: 130 trials, current high-load rate 0.015
previous_trial_correct = 1.0: 1523 trials, current high-load rate 0.670
previous_trial_correct = missing: 30 trials, current high-load rate 0.800
```

This matches the dataset task rule that an incorrect response is followed by a set-size-4 trial. It is not response-time leakage, correctness/match performance leakage, or session/trial-order drift. Because `previous_trial_correct` was predeclared as an allowed behavioral-control covariate, the strongest control remains valid under the current Claim Sheet bar.

## Mechanism State

Claude Session 6 ran `scripts/audit_mtl_coverage.py`. MTL coverage is adequate for all `9/9` subjects. The mechanism gate is open; coverage alone does not support the full deep-readout claim.

Codex Session 8 added the first mechanism scaffold:

- `utils.nix_io.load_ieeg_epochs(...)`: lazy iEEG epoch loader with optional ordered contact selection.
- `utils/mechanism.py`: shared MTL anatomy helper for hippocampus, amygdala, and parahippocampal contacts.
- `scripts/run_mtl_bandpower_probe.py`: computes maintenance-window MTL theta/alpha log power for bundle-retained trials and summarizes load effects plus correlations with supplied scalp decoder scores.

Validation commands from Session 8:

```text
.\venv\Scripts\python.exe -m py_compile utils\nix_io.py utils\mechanism.py scripts\audit_mtl_coverage.py scripts\run_mtl_bandpower_probe.py
.\venv\Scripts\python.exe scripts\audit_mtl_coverage.py --data-dir "D:\Simultaneous EEG_LFP\data_nix" --out-dir outputs\mechanism
.\venv\Scripts\python.exe scripts\run_mtl_bandpower_probe.py --data-dir "D:\Simultaneous EEG_LFP\data_nix" --bundle outputs\features\feature_bundle.npz --signal-predictions outputs\decoding\predictions_tangent_cov_all.csv --out-dir outputs\mechanism
```

Session 8 MTL band-power probe results on `tangent_cov_all`:

```text
MTL theta load effect z:              mean  0.120, 5/9 positive, p2=0.3242
MTL alpha load effect z:              mean  0.025, 5/9 positive, p2=0.8086
MTL theta-minus-alpha load effect z:  mean  0.143, 7/9 positive, p2=0.0156
corr(tangent score, MTL theta):       mean -0.011, 5/9 positive, p2=0.8711
corr(tangent score, MTL alpha):       mean -0.018, 3/9 positive, p2=0.8164
corr(tangent score, theta-alpha):     mean -0.015, 5/9 positive, p2=0.8086
```

Interpretation: the intracranial MTL layer has a real-looking theta-minus-alpha load substrate, but the completed tangent scalp decoder score is not visibly tied to it. This supports continuing mechanism work; it does not satisfy the Claim Sheet mechanism half. Do not draft or apply a Claim Sheet amendment until EEGNet and fuller mechanism evidence are both available and aligned with Claude.

## Active Chat State

Active thread:

- `chats/Claude-Codex/Riemannian Ladder Verdict/Riemannian Ladder Verdict - Active.md`

Session 7 Codex reply:

- Claude should run one bounded EEGNet rung because it was predeclared and completes the model ladder.
- Claude should start mechanism coupling scaffold now that the coverage gate is `9/9`.
- Codex treats the behavioral-control ablation as answered.
- No Claim Sheet amendment should be drafted until EEGNet and first mechanism evidence are both available.

Session 8 Codex update appended:

- reported the new MTL band-power probe;
- highlighted theta-minus-alpha load effect (`7/9`, p2=`0.0156`);
- emphasized that tangent decoder scores do not correlate with MTL theta/alpha summaries;
- asked that EEGNet predictions, when available, go through controls/statistics and this MTL probe before amendment discussion.

No newer Claude response was present at Session 8 closeout.

## Session 8 Progress Report

Codex Session 8 triggered the every-eighth-session progress-report requirement. The report exists at:

- `agents/Codex/Progress Reports/Codex Progress Report - Session 8.md`

It summarizes Sessions 1-8 for a generalist reader: Phase 1 scoping, controls/statistics, negative decoding results so far, behavioral-control explanation, and the first limited mechanism signal.

## Git Closeout State

Codex Session 8 attempted to stage the uncommitted Session 7 files before doing new work, but `git add` still failed:

```text
fatal: Unable to create '.../.git/index.lock': Permission denied
```

There is no stale project `.git/index.lock`. The blocker is repository metadata write permission in this environment.

Uncommitted Codex Session 7 files remain:

- `scripts/run_behavioral_control_ablation.py`
- `agents/Codex/Session Summaries/HumanReport7.md`
- `agents/Codex/README.md`
- `agents/Codex/Summary of Only Necessary Context.md`
- `chats/Claude-Codex/Riemannian Ladder Verdict/Riemannian Ladder Verdict - Active.md`

Additional Codex Session 8 files/edits now also remain uncommitted:

- `utils/nix_io.py`
- `utils/mechanism.py`
- `scripts/audit_mtl_coverage.py`
- `scripts/run_mtl_bandpower_probe.py`
- `agents/Codex/Progress Reports/Codex Progress Report - Session 8.md`
- `agents/Codex/Session Summaries/HumanReport8.md`
- `agents/Codex/README.md`
- `agents/Codex/Summary of Only Necessary Context.md`
- `chats/Claude-Codex/Riemannian Ladder Verdict/Riemannian Ladder Verdict - Active.md`

Pre-existing untracked files not owned by Codex Session 8:

- `scripts/run_eegnet_decoder.py`
- `utils/eegnet.py`

If git metadata write access becomes available, first review the full diff. Stage Codex-owned Session 7+8 files only, and do not include the EEGNet files unless it is clear Claude intended them to be committed in the same closeout.

## Hard Guards To Preserve

- Held-out subject is scored once; all model/feature/window choices happen inside training subjects only.
- Adjacent windows from the same trial cannot straddle train/test boundaries.
- Behavioral-only control must exclude set size, `load_binary`, and every set-size-encoding variable.
- Timing-only control must not include response time, correctness, match/mismatch, neural features, or target encodings.
- A1/A2 are ear/mastoid references; brain-only diagnostics are required but cannot move the headline bar after results are observed.
- Mechanism full-claim support requires adequate MTL coverage and actual coupling evidence, not coverage alone.
- The Session 8 MTL band-power probe is exploratory scaffolding, not a full mechanism success result.
- No raw dataset files, large binaries, generated outputs, scratch probes, local lock files, or local venv files should be committed.

## Next Actions

For Codex:

1. At startup, read the active `Riemannian Ladder Verdict` chat and check whether Claude has responded or produced EEGNet outputs.
2. If EEGNet prediction/subject-score outputs exist, run `scripts/run_control_models.py`, `scripts/summarize_subject_statistics.py`, and `scripts/render_verification_dashboard.py` on that exact rung before interpretation.
3. Rerun `scripts/run_mtl_bandpower_probe.py` against EEGNet predictions once they exist.
4. Extend the mechanism layer beyond band power toward the fuller theta-alpha/coupling analysis named in the Claim Sheet.
5. If EEGNet also fails and mechanism evidence remains meaningful, open an amendment discussion in chat. Do not unilaterally edit the Claim Sheet.
6. If git metadata write access works, carefully stage/commit Codex-owned accumulated work while preserving any unrelated/pre-existing dirty files.

## Local Substrate Facts

- Dataset path: `D:\Simultaneous EEG_LFP`.
- Project virtual environment exists at `.\venv`; always use `.\venv\Scripts\python.exe` and `.\venv\Scripts\pip.exe`.
- Common maintenance timing is fixed across trials: fixation `-6 s`, encoding `-5 s`, maintenance `-3 s`, probe `0 s`.
- iEEG data arrays are trial-aligned, typically shaped `(n_contacts, 16000)`, sampled at `2000 Hz`, and offset `-6 s` relative to probe.
- Local MiKTeX `pdftotext` failed during Session 7 with a MiKTeX configuration error; no PDF parser library is installed in the venv. If the dataset paper must be fully extracted later, install/use an approved parser in the project environment or fix the local PDF tool.
