# Codex Session 6 Report

**Current Date and Time:** 2026-06-11 12:20 PDT

## Summary

This session picked up after Claude's Phase 2 controls-interface handoff. The repository's actual state showed `main` at `Claude Session 5`, with Phase 2 still open and the `Phase 2 Controls Interface` chat concluded. The available local generated artifacts included Claude's first signal-model outputs for the locked 8-channel common montage. Codex's task was therefore to implement the controls/statistics/dashboard lane promised in the Claim Sheet and Codex controls spec.

I created three new reproducibility scripts:

- `scripts/run_control_models.py`
  - Runs the non-signal controls on the same LOSO folds as the signal model.
  - Implements label-shuffle, behavioral-only, timing-only, and within-training subject-identity diagnostics.
  - Hard-fails if forbidden target-encoding columns enter behavioral or timing controls.
  - Emits combined per-trial prediction rows plus per-subject control scores.
- `scripts/summarize_subject_statistics.py`
  - Computes each subject's strongest non-signal control.
  - Computes improvement as `signal_ba - strongest_control_ba`.
  - Evaluates all three predeclared Claim Sheet success criteria.
  - Emits exact subject-level sign-flip evidence, a subject-bootstrap interval, and leave-one-subject-removed robustness.
- `scripts/render_verification_dashboard.py`
  - Renders an initial static HTML dashboard from the prediction/statistics tables.
  - Marks mechanism evidence as not yet available, because the iEEG/MTL coupling layer has not been run.

## Controlled Result

I ran the new scripts against the current headline signal rung:

```text
logistic_all_all
```

This is the logistic all-features, all-8-common-channel signal model from Claude's output. With 100 label-shuffle fits per held-out subject, the controlled result was:

- mean signal balanced accuracy: `0.560`;
- mean strongest-control balanced accuracy: `0.593`;
- mean improvement: `-0.033`;
- subjects above strongest control: `3/9`;
- minimum leave-one-subject-removed mean improvement: `-0.042`;
- subject sign-flip p(one-sided mean >= observed): `0.9590`;
- subject-bootstrap 95% CI for mean improvement: `[-0.063, -0.004]`;
- headline success criteria met: `no`.

The strongest control was behavioral-only for all 9 subjects. This is the central scientific outcome of the session: the first logistic/all-features signal rung does not merely fall short of the `+0.075` improvement bar; it underperforms the behavioral-only control on average.

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

This does not close Phase 2, because Claude's stronger model-ladder rungs may still be worth testing. It does block any success claim for this first logistic/all-features rung. Future signal rungs should be passed through the same controls/statistics scripts before interpretation.

## Challenges and Decisions

The first controls run used 200 label-shuffle fits per subject and timed out after three minutes. The issue was practical rather than conceptual: the script was refitting the signal scaler inside every shuffle loop and scikit-learn future warnings were flooding stdout. I patched the script to fit the scaler once per held-out fold, suppress expected sklearn future warnings, and set the default label-shuffle count to 100. The rerun completed successfully and records `label_shuffle_n=100` in the output table.

The in-app browser refused to open the generated `file://` dashboard path under its URL security policy. I did not try to route around that. Instead, I ran a local HTML parser sanity check, which confirmed the generated dashboard has the expected title, summary block, and nine subject panels. A future session can visually inspect the dashboard through an allowed local HTTP route only if that is approved by the browser policy and needed for the deliverable.

The subject-identity diagnostic returned `1.000` balanced accuracy inside training subjects for every outer fold. That is not a LOSO leak by itself, because held-out subjects are still excluded from training, but it confirms the signal feature space is strongly subject-specific. This reinforces the need to keep LOSO as the headline and to interpret any future neural gain conservatively.

## Files Created or Updated

Created:

- `scripts/run_control_models.py`
- `scripts/summarize_subject_statistics.py`
- `scripts/render_verification_dashboard.py`
- `agents/Codex/Session Summaries/HumanReport6.md`

Updated:

- `agents/Codex/Phase 2 Controls and Statistics Spec.md`
- `agents/Codex/README.md`
- `agents/Codex/Summary of Only Necessary Context.md`

Generated but ignored by git:

- `outputs/controls/control_predictions_logistic_all_all.csv`
- `outputs/controls/control_subject_scores_logistic_all_all.csv`
- `outputs/statistics/subject_statistics_logistic_all_all.csv`
- `outputs/statistics/summary_logistic_all_all.json`
- `outputs/statistics/summary_logistic_all_all.md`
- `outputs/dashboard/verification_dashboard_logistic_all_all.html`

## Validation

Commands run successfully:

```text
.\venv\Scripts\python.exe -m py_compile scripts\run_control_models.py scripts\summarize_subject_statistics.py scripts\render_verification_dashboard.py

.\venv\Scripts\python.exe scripts\run_control_models.py --bundle outputs\features\feature_bundle.npz --metadata outputs\features\feature_metadata.csv --signal-predictions outputs\decoding\predictions_logistic_all_all.csv --signal-subject-scores outputs\decoding\subject_scores_logistic_all_all.csv --out-dir outputs\controls --model logistic --feature-family all --channel-set all --n-shuffles 100 --seed 7

.\venv\Scripts\python.exe scripts\summarize_subject_statistics.py --control-subject-scores outputs\controls\control_subject_scores_logistic_all_all.csv --out-dir outputs\statistics --seed 7

.\venv\Scripts\python.exe scripts\render_verification_dashboard.py --predictions outputs\controls\control_predictions_logistic_all_all.csv --subject-statistics outputs\statistics\subject_statistics_logistic_all_all.csv --summary outputs\statistics\summary_logistic_all_all.json --out-dir outputs\dashboard
```

Local HTML sanity check passed:

```text
{'h1': 'EEG to LFP Verification Dashboard', 'subject_panels': 9, 'has_summary_grid': True, 'bytes': 228523}
```

## Git Closeout Status

The session changes could not be staged, committed, or pushed because `git add` failed:

```text
fatal: Unable to create '.../.git/index.lock': Permission denied
```

I checked for a stale `.git/index.lock`; none exists. This matches the repository-metadata write restriction previously observed by Codex. The project files listed above are updated in the working tree but remain uncommitted.

## Next Steps

The next Codex session should run these same scripts against any new signal rung Claude emits. If behavioral-only remains dominant, Codex should add a control-ablation report that separates response-time, correctness/match, previous-trial, and trial-order/session effects. That will help determine whether the behavioral control is exposing a real task-structure confound or simply a strong non-neural correlate that future neural models must beat.

The mechanism layer remains pending. Until MTL coupling summaries exist, the dashboard should continue to mark mechanism evidence as unavailable and should not label any subject as final support for the full deep-readout claim.
