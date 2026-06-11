# Phase 2 Controls and Statistics Spec - Codex

**Session:** Codex Session 4; updated Codex Sessions 5-6
**Last updated:** 2026-06-11 12:18 PDT
**Status:** Controls/statistics/dashboard scripts implemented for the first signal rung. The logistic/all-features/all-channel headline signal result has been compared against controls and does **not** meet the Claim Sheet success criteria.

This document defines the controls/statistics interface Codex will need once Claude's Phase 2 data layer exposes aligned scalp epochs, task metadata, and later iEEG/unit mechanism inputs. It is intentionally a spec first, not a harness implementation, because the Claim Sheet requires a trial-count audit before any model result is observed.

## Locked pre-model decision after Claude Session 4 audit

Claude Session 4 produced `outputs/trial_count_audit.md` and `outputs/montage_intersection.json` before any decoder was fit. Codex reviewed the audit in Session 5 and locked the following configuration for the headline decoding run:

- The predeclared `+0.075` mean balanced-accuracy improvement bar stands. The count audit found no empty classes, no class below 10 included trials, no subject above 3:1 high/low imbalance, and no subject above 20% artifact exclusions.
- Headline LOSO signal features must use only the common physical scalp montage present in all 9 subjects: `A1`, `A2`, `C3`, `C4`, `F3`, `F4`, `O1`, `O2`.
- Missing-channel padding, imputation, or per-subject feature expansion is forbidden for the headline LOSO result. Extra channels in richer-montage subjects may be used only for within-subject or other clearly labeled diagnostics.
- Because `A1` and `A2` are ear/mastoid reference channels, feature extraction must preserve channel-role metadata. The final artifact-sanity report should include a common-brain-channel sensitivity diagnostic excluding `A1`/`A2` (`C3`, `C4`, `F3`, `F4`, `O1`, `O2`). This diagnostic cannot replace the locked headline result or move the success bar after results are observed, but a headline result dominated by `A1`/`A2` must be discussed as a reference/artifact risk.

## Codex Session 6 implementation and first control result

Codex Session 6 implemented the first controls/statistics/dashboard lane:

- `scripts/run_control_models.py` consumes `outputs/features/feature_bundle.npz`, `outputs/features/feature_metadata.csv`, and a signal prediction/score pair. It runs the label-shuffle, behavioral-only, and timing-only controls on the same LOSO folds as the signal model; hard-fails if forbidden target columns enter non-signal controls; and emits a within-training subject-identity diagnostic.
- `scripts/summarize_subject_statistics.py` computes the Claim Sheet success criteria from subject-level improvements over the strongest non-signal control, including exact sign-flip evidence, subject-bootstrap interval, and leave-one-subject-removed robustness.
- `scripts/render_verification_dashboard.py` renders an initial static HTML dashboard from the prediction/statistics tables. The current dashboard is decoding-only because the mechanism layer has not been run.

Smoke-test command sequence used the existing ignored artifacts:

```text
.\venv\Scripts\python.exe scripts\run_control_models.py --bundle outputs\features\feature_bundle.npz --metadata outputs\features\feature_metadata.csv --signal-predictions outputs\decoding\predictions_logistic_all_all.csv --signal-subject-scores outputs\decoding\subject_scores_logistic_all_all.csv --out-dir outputs\controls --model logistic --feature-family all --channel-set all --n-shuffles 100 --seed 7
.\venv\Scripts\python.exe scripts\summarize_subject_statistics.py --control-subject-scores outputs\controls\control_subject_scores_logistic_all_all.csv --out-dir outputs\statistics --seed 7
.\venv\Scripts\python.exe scripts\render_verification_dashboard.py --predictions outputs\controls\control_predictions_logistic_all_all.csv --subject-statistics outputs\statistics\subject_statistics_logistic_all_all.csv --summary outputs\statistics\summary_logistic_all_all.json --out-dir outputs\dashboard
```

First controlled result for `logistic_all_all`:

- mean signal balanced accuracy: `0.560`;
- mean strongest-control balanced accuracy: `0.593`;
- mean improvement: `-0.033`;
- subjects above strongest control: `3/9`;
- minimum leave-one-subject-removed mean improvement: `-0.042`;
- headline success criteria met: `no`;
- the strongest control is behavioral-only for all 9 subjects.

Interpretation: this does not close the project, because Claude's model ladder can still test stronger signal models, but it blocks any success claim for the first logistic/all-features rung. Future rungs must be passed through the same controls/statistics scripts before being compared to the Claim Sheet bar.

## Hard guards before modeling

1. **Trial-count audit first.** Count maintenance-period trials per subject and set size before fitting any decoder or control model. If the counts make the predeclared +0.075 balanced-accuracy improvement bar questionable, open a new Claude-Codex chat and agree a replacement bar before any model run.
2. **Held-out subject touched once.** For each LOSO fold, all channel choices, feature choices, windows, thresholds, hyperparameters, and calibration decisions must be fixed using training subjects only.
3. **No window leakage.** If multiple windows are created from one trial, every window from a trial must stay in the same train/test side. Subject metrics should be reported at the trial level or as a clearly named window-aggregated diagnostic.
4. **Behavioral-only excludes the label.** No set size, high/low label, stimulus count, or derived variable that encodes set size may enter the behavioral-only control.
5. **No silent exclusions.** Every dropped subject, session, trial, channel, or feature family must be listed with a reason in a machine-readable exclusions table and in the human-readable summary.

## Required data-layer outputs

Claude's reader can choose its internal implementation, but Codex needs the following stable outputs from the aligned epoch layer.

### Trial metadata table

One row per trial, before windowing. Required columns:

| Column | Purpose |
| --- | --- |
| `subject_id` | LOSO grouping key. |
| `session_id` | Session grouping and behavioral/timing covariate. |
| `trial_id` | Stable trial identifier unique within subject/session. |
| `trial_index` | Original within-session order. |
| `set_size` | Ground-truth load, values expected to be 4, 6, or 8. Not allowed in behavioral-only controls. |
| `load_binary` | Primary target: 0 for set size 4, 1 for set sizes 6/8. Not allowed in controls. |
| `match` | Probe match/mismatch covariate. |
| `correct` | Correct/incorrect covariate. |
| `response` | Button/choice response if available. |
| `response_time_s` | Response time in seconds. |
| `encoding_onset_s` | Trial-relative encoding onset. |
| `maintenance_onset_s` | Trial-relative maintenance onset. |
| `maintenance_offset_s` | Trial-relative maintenance offset. |
| `probe_onset_s` | Trial-relative probe/recall onset. |
| `scalp_sample_rate_hz` | Expected 200 Hz after dataset resampling. |
| `ieeg_sample_rate_hz` | Expected 2000 Hz when available. |
| `trial_rejected` | Boolean. |
| `rejection_reason` | Empty for included trials; explicit reason otherwise. |

Recommended columns:

- `previous_trial_correct`, because the task paper states incorrect trials are followed by set-size-4 trials; this may expose a trial-order confound that controls should audit.
- `absolute_trial_start_s` or equivalent acquisition clock if available, for timing-only checks.
- `scalp_channel_labels`, `scalp_channel_status`, and `reference_label` either as columns or linked sidecar metadata.
- `mtl_contact_labels`, `mtl_anatomical_labels`, and `mtl_coverage_flag` for the later mechanism coverage audit.

### Epoch/window metadata table

One row per analysis window after epoching. Required columns:

| Column | Purpose |
| --- | --- |
| `epoch_id` | Stable window identifier. |
| `subject_id`, `session_id`, `trial_id` | Join keys back to trial metadata. |
| `epoch_name` | `maintenance` for the headline analysis; other epochs are diagnostics. |
| `epoch_start_s`, `epoch_end_s` | Trial-relative epoch/window bounds. |
| `window_index` | Index if multiple windows are cut from one trial. |
| `is_primary_epoch` | True only for the predeclared maintenance headline windows. |
| `included_for_primary` | True only if usable for headline trial-count and modeling. |
| `exclusion_reason` | Empty when included. |

### Feature bundle contract

For any decoder/control script, the preferred serialized bundle should include:

- `X_signal`: numeric feature matrix for scalp-derived features only.
- `y`: primary target vector (`load_binary` for headline).
- `groups.subject_id`, `groups.session_id`, `groups.trial_id`: grouping arrays.
- `metadata`: table containing all trial/window metadata needed for controls and reporting.
- `feature_names`: stable names with channel, band, statistic, and window encoded.
- `feature_family`: e.g. `band_power`, `covariance`, `coupling`, `behavioral`, `timing`.
- `channel_names` and `band_names`.
- `exclusions`: table of dropped rows/channels/features with reasons.

Codex can adapt to file format, but `parquet`, `csv` plus `npz`, or HDF5 are easiest to audit. Pick one format and document it in the packet README.

## Control definitions

All controls use the same LOSO folds as the signal model. Hyperparameters must be selected using training subjects only.

### Label-shuffle control

Purpose: estimate whether the pipeline can produce apparent decoding without a real feature-label relationship.

Rules:

- Shuffle labels only inside the training portion of each LOSO fold.
- Preserve training-subject/session class structure where feasible. The conservative default is to shuffle within `(subject_id, session_id)` strata if both classes exist, otherwise within `subject_id`.
- Do not shuffle held-out labels.
- Report a fixed random seed and the number of permutations.
- Final reporting should use enough permutations for a stable interval; development runs can use fewer and must be labeled as development.

### Behavioral-only control

Purpose: quantify how much load can be inferred from non-signal covariates.

Allowed input families:

- `response_time_s`
- `correct`
- `match`
- `session_id`
- `trial_index`
- timing columns that do not encode set size
- `previous_trial_correct` if available

Forbidden input families:

- `set_size`
- `load_binary`
- stimulus count, memory-list length, or any encoding of the target
- any scalp, iEEG, LFP, unit, artifact-channel, or signal-derived feature
- any post-hoc feature created using the target label

### Timing-only control

Purpose: guard against decoding the task scaffold rather than neural state.

Allowed inputs:

- trial/epoch timing variables
- session and trial order variables
- acquisition-clock variables if available

Forbidden inputs:

- response time, correctness, match/mismatch
- target labels or set-size encodings
- all neural signal features

### Subject-identity and artifact checks

The headline LOSO split prevents train/test subject overlap, but subject identity can still dominate features and make generalization brittle. Report:

- within-training subject-ID classification from signal features as a diagnostic;
- per-subject feature distribution summaries;
- any feature family or channel whose importance is dominated by one subject;
- artifact-channel or obvious non-neural feature dominance if those channels exist.

## Metrics and evidence

Primary unit of evidence is the held-out subject.

For each held-out subject:

1. Compute balanced accuracy for the signal model.
2. Compute balanced accuracy for each non-signal control.
3. Define `strongest_control_ba` as the maximum of behavioral-only, timing-only, and label-shuffle control balanced accuracy for that subject.
4. Define `improvement` as `signal_ba - strongest_control_ba`.

Headline success requires all three Claim Sheet conditions:

- mean subject improvement >= 0.075;
- at least 7 of 9 held-out subjects have improvement > 0;
- no leave-one-subject-out removal drops mean improvement below 0.04.

Subject-level uncertainty:

- Report the exact sign-flip null over the 9 subject improvements when possible.
- Report a subject-level interval for mean improvement.
- Window-level or trial-level permutation can be included as a diagnostic only; it cannot substitute for subject-level evidence.

## Trial-count audit output

The first Phase 2 audit should produce a table and a short human-readable summary before any model run.

Required counts:

- included trials by `subject_id`, `session_id`, and `set_size`;
- included trials by `subject_id` and `load_binary`;
- rejected trials by subject/session/reason;
- class imbalance by held-out subject;
- number of available maintenance windows per trial if windowing is already defined.

Discussion triggers, not automatic amendments:

- any subject has zero trials in either binary class;
- any subject has fewer than 10 included trials in either binary class;
- any subject's high/low class ratio exceeds 3:1;
- primary exclusions remove more than 20% of trials for a subject;
- counts disagree with dataset metadata or the MATLAB/NIX reference documentation.

If any trigger fires, Claude and Codex should discuss whether the +0.075 bar remains fair before any decoder is fit.

## Verification dashboard input contract

Codex's dashboard renderer will need a fold-level predictions table:

| Column | Purpose |
| --- | --- |
| `subject_id`, `session_id`, `trial_id` | Joins and display. |
| `set_size`, `load_binary` | Ground truth display. |
| `signal_pred`, `signal_score` | Scalp-only prediction and score. |
| `behavioral_pred`, `behavioral_score` | Behavioral-only control. |
| `timing_pred`, `timing_score` | Timing-only control. |
| `shuffle_summary` | Aggregate label-shuffle result for the fold/trial or fold. |
| `strongest_control` | Which control won for the subject. |
| `support_label` | `support`, `weaken`, or `contradict`, using the final verdict rules. |
| `mechanism_available` | True once mechanism data exists for this subject. |
| `mechanism_summary` | Human-readable mechanism result or reason unavailable. |

Initial verdict rules can be decoding-only. Final verdict rules must incorporate the mechanism layer:

- `support`: subject beats strongest control and mechanism evidence is available and directionally consistent.
- `weaken`: subject beats controls but mechanism is absent, sparse, or inconclusive.
- `contradict`: subject does not beat strongest control, or mechanism evidence actively opposes the deep-readout interpretation.

## Likely script boundaries once the data layer exists

Names are provisional; keep one purpose per script.

- `audit_trial_counts.py`: consumes aligned trial metadata and writes the pre-model trial-count audit.
- `make_loso_splits.py`: emits fold definitions and validates no subject/window leakage.
- `run_control_models.py`: trains/evaluates label-shuffle, behavioral-only, and timing-only controls.
- `summarize_subject_statistics.py`: computes subject-level improvements, sign-flip evidence, and robustness checks.
- `render_verification_dashboard.py`: consumes predictions and mechanism summaries to produce the director-facing dashboard.

All scripts should use `argparse`, require machine-specific inputs explicitly, print progress, write named outputs, and fail loudly on missing columns or forbidden control inputs.
