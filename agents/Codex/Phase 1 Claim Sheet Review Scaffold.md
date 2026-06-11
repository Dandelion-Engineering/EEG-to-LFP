# Phase 1 Claim Sheet Review Scaffold - Codex

**Author:** Codex
**Created:** 2026-06-11
**Status:** Codex-owned review aid; not a Claim Sheet and not a Phase 0 closure.

## Purpose

This scaffold records what Codex should check when Claude drafts the Phase 1 Claim Sheet. Claude remains the default writer for the Claim Sheet and Accessible Claim Sheet. Codex's role is to pressure-test the proposed technical contract before execution begins, with special attention to leakage, target construction, reproducibility, licensing, and whether the first claim is small enough to validate honestly.

The expected first-rung frame is:

> Scalp EEG contains a subject-transferable signature of an intracranially validated MTL working-memory state in the simultaneous EEG/iEEG verbal working-memory dataset.

Candidate A, scalp-only prediction of an intracranially validated working-memory or deep-state target, should be the primary first rung unless Claude identifies a stronger reason to start with Candidate B. Candidate B, scalp-to-MTL theta/alpha band-power time-course reconstruction, should remain a fast-follow or predeclared extension. Full waveform reconstruction and unit-level inference should be diagnostic or later-rung work, not the first headline.

## Claim Sheet Gates

### 1. Target Construction

The Claim Sheet must state the primary target in enough detail that a future implementation cannot quietly change it after seeing results.

Required decisions:

- Is the primary target working-memory load or an iEEG-derived deep-state label?
- If working-memory load is primary, is the target multiclass set size, high-versus-low load, or regression on set size?
- If a deep-state target is primary, which intracranial signal defines it: MTL band power, hippocampal-cortical coupling, unit firing, or a region-level aggregate?
- What trial window is used: encoding, maintenance, retrieval, or a predeclared combination? If working-memory load is primary, the headline should privilege the maintenance period so the model cannot win by reading visual stimulus-load cues during encoding.
- Are incorrect trials excluded, modeled separately, or retained with a behavioral covariate?
- Are seizure-onset-zone contacts excluded from target construction, used with sensitivity analysis, or retained?
- How are subjects or sessions with missing or unsuitable targets handled?

Leakage guard:

- The target must not be defined from the same scalp features used as predictors. If scalp-to-hippocampal coupling is used, the Claim Sheet must explain how predictor-target circularity is avoided.
- Any thresholds, channel choices, region summaries, or feature selection rules must be derived from training subjects only inside each subject-held-out fold.

### 2. Split Design

The headline evaluation should hold out whole subjects.

Minimum acceptable design:

- Leave-one-subject-out across the 9 subjects, or a clearly justified subject-held-out variant.
- All sessions and all windows from the held-out subject stay out of training, validation, feature selection, normalization fitting, and hyperparameter tuning.
- Hyperparameters are selected inside the training subjects only, preferably with nested subject-wise validation.
- Any within-subject split is labeled diagnostic and cannot support the transferable claim.
- Adjacent windows from the same trial cannot be split across train and test in the headline result.

The Claim Sheet should require per-subject reporting. A mean score alone is not acceptable with only 9 subjects.

### 3. Controls

The Claim Sheet should predeclare controls that distinguish scalp signal from task timing, behavior, identity leakage, and chance structure.

Minimum controls:

- Label-shuffled control performed inside the same training/evaluation scaffold.
- Behavioral-only control using non-signal covariates such as response time, correctness, match/mismatch, session, and trial order, but not the target label itself. If the target is working-memory load or set size, the control must explicitly exclude set size and any derived variable that encodes it.
- Timing-only control using trial phase/window timing but no scalp signal or outcome-relevant behavioral variables.
- Subject/session leakage check, where applicable, to catch hidden identity or session artifacts.
- Autocorrelation/window leakage check for any overlapping-window analysis.
- Scalp artifact sanity check to ensure eye, muscle, bad-channel, or reference artifacts are not carrying the result.

Useful ablations:

- Theta/alpha-only versus broadband features.
- Parietal channel emphasis, including P3/Pz neighborhood, versus all channels.
- Maintenance-only versus encoding/retrieval windows.
- Simple feature/model baselines versus any neural model.

### 4. Model Ladder

The first executable plan should start with compact, inspectable models.

Preferred initial ladder:

1. Band-power and log-variance features with regularized linear or logistic models.
2. Filter-bank covariance features with shrinkage LDA or ridge/logistic regression.
3. Riemannian covariance classifier or regressor if dependency/licensing checks are clean.
4. EEGNet or another compact CNN only after simple baselines are frozen.
5. Foundation-model embeddings only as a later comparison after license, checkpoint provenance, and 8 GB VRAM fit are verified.

The Claim Sheet should not require NeuroFlowNet-style conditional normalizing flows for the first rung. NeuroFlowNet is prior art and a possible later diagnostic, not the baseline contract.

### 5. Metrics And Result Shapes

Metrics must match the target type and support the declared success, failure, and inconclusive shapes.

Classification candidates:

- Balanced accuracy, macro F1, AUROC where applicable, and calibration if probabilities are interpreted.
- Per-subject score table and fold plot.
- Permutation or bootstrap confidence intervals at the subject/fold level.

Regression or reconstruction candidates:

- Correlation against true iEEG-derived target, mean absolute error or normalized error, and control-relative improvement.
- Per-subject and per-region results, not only pooled windows.
- Frequency-band-specific metrics if reconstructing band power.

Success should require performance above controls in a way that is not carried by one subject. Failure should include the case where within-subject models work but subject-held-out models collapse. Inconclusive should include target sparsity, missing coverage, or subject variance too large for a stable claim.

### 6. Verification Artifact

The director-facing verification artifact should make the result auditable without requiring domain expertise.

Preferred artifact:

- One static report or lightweight dashboard over the 9 held-out folds.
- For each held-out subject: target definition, scalp input feature summary, true target trajectory or labels, model prediction, control predictions, and a brief interpretation.
- A clear "supports / weakens / contradicts" indicator per subject.
- A leakage-control panel showing that timing-only, behavior-only, and shuffled controls do not explain the headline result.

The artifact must avoid cherry-picked single examples. It can include illustrative examples, but the fold-level summary is the evidence.

### 7. Licensing And Release Policy

The Claim Sheet must explicitly handle the dataset's CC BY-SA 4.0 status.

Minimum policy:

- Raw data stays outside the repository and is not redistributed.
- Public reports and figures include dataset attribution and license notice.
- Derived datasets, cached features, model weights, and example data snippets are treated as ShareAlike-sensitive unless the Claim Sheet records a narrower legal interpretation.
- Dandelion-written code can use a permissive license if it does not embed adapted dataset material.
- Any third-party package, pretrained model, or copied code must permit commercial use before adoption.

### 8. Reproducibility And Environment

The Claim Sheet should preserve the Dandelion standards from the start.

Required implementation constraints:

- Use `.\venv\Scripts\python.exe` and `.\venv\Scripts\pip.exe` only.
- Pin dependencies in `requirements.txt` when implementation begins.
- Every script accepts paths through `argparse`; no hard-coded local data path in scripts.
- Outputs default to project-relative locations.
- Dataset path is passed as a CLI argument, with `D:\Simultaneous EEG_LFP` only documented as the director's current local path.
- Exclusion rules for subjects, sessions, contacts, channels, trials, and windows are written to output files.

## Questions To Resolve Before Execution

1. Should the primary target be working-memory load with intracranial validation, or an iEEG-derived deep-state label?
2. Which MTL structures have enough coverage across subjects for a comparable target?
3. What is the SOZ-contact policy for target construction and sensitivity analysis?
4. Are we using all correct trials, all trials with correctness covariates, or correct trials only?
5. Does the first rung include a small subject-specific diagnostic baseline, or is the first implementation exclusively subject-held-out?
6. What exact artifact license policy applies to derived features, trained weights, and public figures?
7. What minimum effect over controls counts as success, and how much subject-to-subject variance still counts as inconclusive?

## Minimal Acceptance Checklist

Codex should approve the Claim Sheet only if it clearly answers:

- The first transferable claim is modest, testable, and not direct field recovery.
- The headline split holds out subjects.
- The target cannot leak scalp predictors into labels.
- Controls include shuffled, timing-only, behavioral-only, and leakage checks.
- Metrics and success/failure/inconclusive shapes are predeclared.
- The model ladder starts with transparent, low-compute baselines.
- CC BY-SA release handling is explicit.
- The director verification artifact is defined.
- Implementation rules preserve reproducibility from the first script.
