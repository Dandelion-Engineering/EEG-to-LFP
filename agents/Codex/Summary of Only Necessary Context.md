# Summary of Only Necessary Context - Codex

**Last rewritten:** 2026-06-11 12:18 PDT (Codex Session 6)
**Current phase:** Phase 2 - Execution open

Re-read `AgentPrompt.md`, `Project Details/Project Details.md`, the Claim Sheet pair, and Codex-related chat summaries at the start of the next session. This file only records Codex-specific continuity not already contained there.

## Current project state

Phase 0 and Phase 1 are closed. The technical Claim Sheet is agent-approved rev. 2, `Accessible Claim Sheet.md` exists, and `director_requests.md` still has Request 1 asking Randy to review the Claim Sheet pair. That request is non-blocking.

Phase 2 remains open. Claude owns the data layer and primary signal model ladder. Codex owns controls, subject-level statistics, and dashboard rendering. The concluded `chats/Claude-Codex/Phase 2 Controls Interface/` thread is the latest Claude-Codex handoff.

## Locked headline configuration

The raw-sparse montage screen remains locked:

- headline LOSO scalp features use only the 8 common physical scalp channels: `A1`, `A2`, `C3`, `C4`, `F3`, `F4`, `O1`, `O2`;
- missing-channel padding, imputation, and subject-specific expanded feature spaces are forbidden for the headline result;
- `A1`/`A2` are ear/mastoid references, so the common-brain-channel diagnostic excluding them (`C3`, `C4`, `F3`, `F4`, `O1`, `O2`) remains predeclared and cannot move the success bar after results are observed;
- the Claim Sheet success bar remains `+0.075` mean LOSO balanced-accuracy improvement over strongest non-signal control, at least `7/9` subjects above control, and no leave-one-subject-removed mean below `0.04`.

## Available Phase 2 artifacts

Generated outputs are intentionally ignored by git under `/outputs/`, but the local workspace currently has:

- `outputs/features/feature_bundle.npz` with `X_signal` shape `1683 x 220`, `y`, subject/session/trial ids, feature names/families, channel roles, and covariance matrices;
- `outputs/features/feature_metadata.csv` / `.parquet`;
- `outputs/features/loso_folds.json` and `loso_fold_assignment.csv`;
- `outputs/decoding/predictions_logistic_all_all.csv` and `subject_scores_logistic_all_all.csv` for the current headline signal rung;
- other first-rung signal diagnostics under `outputs/decoding/`.

Claude's first signal numbers before controls were: logistic band-power 8-ch `0.512`, covariance 8-ch `0.559`, all-features 8-ch `0.560`, and A1/A2-excluded brain-only diagnostic `0.557`.

## Codex Session 6 controls/statistics/dashboard implementation

Codex Session 6 added:

- `scripts/run_control_models.py`: runs label-shuffle, behavioral-only, timing-only, and within-training subject-identity diagnostics on the same LOSO folds as the signal model. It hard-fails if forbidden target columns enter the behavioral or timing control.
- `scripts/summarize_subject_statistics.py`: computes strongest-control improvements, exact subject-level sign-flip evidence, subject-bootstrap interval, and the three Claim Sheet success criteria.
- `scripts/render_verification_dashboard.py`: renders an initial static HTML director dashboard from the prediction/statistics tables. The current dashboard is decoding-only because the mechanism layer is not run yet.

Validation commands from Session 6:

```text
.\venv\Scripts\python.exe -m py_compile scripts\run_control_models.py scripts\summarize_subject_statistics.py scripts\render_verification_dashboard.py
.\venv\Scripts\python.exe scripts\run_control_models.py --bundle outputs\features\feature_bundle.npz --metadata outputs\features\feature_metadata.csv --signal-predictions outputs\decoding\predictions_logistic_all_all.csv --signal-subject-scores outputs\decoding\subject_scores_logistic_all_all.csv --out-dir outputs\controls --model logistic --feature-family all --channel-set all --n-shuffles 100 --seed 7
.\venv\Scripts\python.exe scripts\summarize_subject_statistics.py --control-subject-scores outputs\controls\control_subject_scores_logistic_all_all.csv --out-dir outputs\statistics --seed 7
.\venv\Scripts\python.exe scripts\render_verification_dashboard.py --predictions outputs\controls\control_predictions_logistic_all_all.csv --subject-statistics outputs\statistics\subject_statistics_logistic_all_all.csv --summary outputs\statistics\summary_logistic_all_all.json --out-dir outputs\dashboard
```

The in-app browser refused `file://` navigation to the generated dashboard under its URL policy, so Session 6 did not visually inspect the page in-browser. A local HTML parser sanity check passed: title present, summary grid present, and `9` subject panels present.

## First controlled result

For `logistic_all_all`, controls show the current headline rung does **not** meet the Claim Sheet success bar:

- mean signal balanced accuracy: `0.560`;
- mean strongest-control balanced accuracy: `0.593`;
- mean improvement: `-0.033`;
- subjects above strongest control: `3/9`;
- minimum leave-one-subject-removed mean improvement: `-0.042`;
- subject sign-flip p(one-sided mean >= observed): `0.9590`;
- subject-bootstrap 95% CI for mean improvement: `[-0.063, -0.004]`;
- strongest control is behavioral-only for all 9 subjects.

Per-subject improvements over strongest control:

```text
S01 +0.011
S02 -0.095
S03 -0.073
S04 +0.039
S05 -0.054
S06 -0.001
S07 -0.091
S08 -0.038
S09 +0.003
```

Interpretation: the first logistic/all-features/all-channel rung cannot support the headline claim. This does not close Phase 2 because stronger signal rungs may still be tested, but every future rung must go through the same control/statistics scripts before being compared to the Claim Sheet bar.

## Git closeout status

Codex Session 6 could not stage, commit, or push. `git add` failed with:

```text
fatal: Unable to create '.../.git/index.lock': Permission denied
```

There was no existing `.git/index.lock`, so this is the same repository-metadata write restriction previously observed by Codex. The Session 6 files are updated in the working tree but remain uncommitted. A future session with Git metadata write access should stage them and commit as `Codex Session 6` before adding more work if possible.

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

For Codex:

1. When Claude produces another signal rung's prediction/subject-score pair, run `scripts/run_control_models.py`, `scripts/summarize_subject_statistics.py`, and `scripts/render_verification_dashboard.py` against that exact pair.
2. Inspect why behavioral-only is strong before interpreting any neural result. Candidate covariates to audit include `response_time_s`, `correct`, `match`, `trial_index`, `previous_trial_correct`, and `session_id`; do not add set size or label encodings.
3. Consider adding a control-ablation report if behavioral-only remains dominant: RT-only, correctness/match-only, previous-trial-only, trial-order/session-only.
4. Mechanism layer remains pending. The dashboard should continue to mark mechanism as unavailable until iEEG/MTL coupling summaries exist.
5. Codex Session 8 will trigger the every-eighth-session progress report if the count remains continuous.

For Claude:

1. Continue the model ladder only if useful: filter-bank covariance + shrinkage, Riemannian diagnostic, and later EEGNet-class compact CNN if still justified.
2. Emit each future signal rung in the same prediction/subject-score shape used by `run_control_models.py`.
3. If the feature-output contract changes, open a new Claude-Codex chat before Codex adapts the harness.

## Local substrate facts

- Dataset path: `D:\Simultaneous EEG_LFP`.
- Project virtual environment exists at `.\venv`; always use `.\venv\Scripts\python.exe` and `.\venv\Scripts\pip.exe`.
- Common maintenance timing is fixed across trials: fixation `-6 s`, encoding `-5 s`, maintenance `-3 s`, probe `0 s`.
