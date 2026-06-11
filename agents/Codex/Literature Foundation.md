# Codex Literature Foundation

## Scope of this document

This is Codex's Phase 0 foundation for the EEG-to-LFP project. It is intended to help turn the director's "electrical fMRI" north star into the smallest first claim that can stand on its own.

My bottom line is that the first project should not try to prove direct field recovery from scalp EEG. It should test whether scalp EEG contains a reproducible, subject-held-out signature of a deep, intracranially validated medial temporal lobe (MTL) working-memory state. If that succeeds, the project earns the right to move toward band-limited reconstruction and later waveform reconstruction. If it fails cleanly, it still tells us whether the first rung of the larger idea is present in this dataset.

## Load-bearing context from the local project and dataset

The project idea is to explore whether cheap scalp EEG plus AI can infer more about deep neural activity than conventional interpretation allows. The validation asset is the simultaneous scalp EEG, intracranial EEG, local field potential, and single-unit dataset in `D:\Simultaneous EEG_LFP`.

The downloaded dataset contains:

- 9 epilepsy patients performing a modified Sternberg verbal working-memory task.
- 37 NIX/HDF5 session files in `D:\Simultaneous EEG_LFP\data_nix`.
- Simultaneous 10-20 scalp EEG, depth-electrode iEEG/LFP, spike times and waveforms from 1526 MTL units, electrode MNI coordinates, anatomical labels, trial metadata, and task event timing.
- A MATLAB example loader showing the HDF5/NIX structure: trial-level `iEEG data`, `Scalp EEG data`, `Trial events`, `Spike times`, and `iEEG electrode information` groups.
- A CC BY-SA 4.0 license.

The dataset is large enough to support careful validation, but small enough that most apparent high performance can be fake if the split is wrong. The strongest evaluation rule for Phase 1 is therefore not a model choice. It is a split choice: the headline result must be leave-one-subject-out or otherwise subject-held-out.

## Scientific framing

### 1. Do not frame the first claim as direct deep-source field recovery

Scalp EEG is a volume-conducted, low-spatial-resolution measurement. Deep MTL sources are attenuated, mixed, orientation-dependent, and non-unique under the EEG inverse problem. A scalp pattern can be compatible with many intracranial configurations. This does not make the director's idea impossible, but it changes the honest first claim.

The strongest Phase 1 framing is:

> Scalp EEG may carry indirect, cortex-mediated signatures of MTL state because MTL activity couples with cortical networks during memory.

That framing is materially different from saying:

> Scalp EEG directly measures the MTL field well enough to localize or reconstruct it.

The first statement is testable in the current dataset. The second is too broad for this first project and too easy to overstate.

### 2. The relevant signal is probably a task-state and coupling signature

The Boran et al. working-memory result attached to this dataset is the key biological anchor: hippocampal firing and hippocampal-cortical coupling vary with verbal working-memory load. That means the dataset is not just paired scalp and intracranial data. It is paired data collected during a task where the MTL signal has an interpretable state variable.

For this project, that matters more than generic waveform reconstruction. A classifier or regressor that predicts an intracranially validated working-memory state from scalp EEG is a cleaner first rung than a model that draws plausible iEEG traces but has weak generalization.

### 3. The first rung should privilege transfer over within-subject fidelity

Within-subject models can answer useful engineering questions: can a subject-specific map from scalp to iEEG be fit at all? But a subject-specific result is not enough for Dandelion's downstream goal. The affordable-technology direction needs a result that transfers across people, at least weakly.

Because there are only 9 subjects, transfer will be noisy. That is acceptable if Phase 1 predeclares the result shapes:

- Success: subject-held-out performance is above strong controls with uncertainty intervals that do not collapse to chance.
- Failure: within-subject performance exists but subject-held-out performance fails, implying subject-specific calibration is required or this dataset cannot support a transferable first claim.
- Inconclusive: variance is too high across the 9 subjects or too many subjects lack comparable MTL targets.

### 4. NeuroFlowNet is important prior art, but it should not define the first project

NeuroFlowNet is the closest current prior art I found. It attempts scalp EEG to MTL iEEG reconstruction with a conditional normalizing flow, uses the same public synchronized EEG-iEEG dataset family, and reports waveform, spectral, and inter-channel correlation fidelity. It is recent and directly relevant.

However, it is a poor first target for Dandelion to copy:

- Its strongest reported protocol is subject-specific, not leave-one-subject-out.
- The paper reports training on a single RTX 4080 with 16 GB memory; the project machine has an RTX 4070 Laptop GPU with 8 GB VRAM.
- The task is larger than the first claim needs.
- The GitHub repository visible during this session did not show a clear license on the repository page, so code reuse should be avoided unless a permissive license is verified.

NeuroFlowNet should influence the Claim Sheet by setting a "do not accidentally underclaim prior art" floor. It should not become the implementation plan for Phase 1.

## Candidate first-rung claims

### Candidate A: scalp-only prediction of an intracranially validated MTL working-memory state

This is my preferred first claim.

Possible concrete target:

> In a subject-held-out evaluation on the simultaneous scalp EEG/iEEG verbal working-memory dataset, scalp EEG predicts an MTL-validated working-memory load or coupling state above behavioral-only, timing-only, and label-shuffled controls.

Why this is the best first rung:

- It tests the central project bet directly: scalp EEG contains information about deep activity beyond conventional interpretation.
- It avoids claiming spatially resolved deep reconstruction too early.
- It can use simple, interpretable models first.
- It gives the director a clear verification artifact: for each held-out subject, show scalp features, true iEEG-derived state, model prediction, and controls.
- It produces reusable infrastructure for later reconstruction: loaders, event alignment, subject splits, feature extraction, target construction, and statistical testing.

The most important design choice is the target definition. I see two plausible primary targets:

- Working-memory load class or set-size regression, validated against iEEG/unit evidence that the MTL state tracks load.
- High versus low hippocampal-cortical coupling or MTL theta/alpha coupling state, derived directly from simultaneous iEEG/scalp or iEEG/cortical relationships.

The first is easier and more legible. The second is closer to the director's deep-signal intuition, but it requires more careful target construction to avoid circularity if scalp channels are used in both target and predictor.

### Candidate B: scalp-to-MTL band-power time-course reconstruction

This is the best fast-follow if Candidate A works or if Phase 1 wants a more reconstruction-shaped first claim.

Possible concrete target:

> Scalp EEG reconstructs held-out-subject MTL theta/alpha band-power dynamics better than subject-, timing-, and shuffled-label controls.

This is closer to "electrical fMRI in miniature" because it reconstructs a continuous deep signal summary. It is still far safer than full waveform reconstruction because band power is lower-dimensional, more robust, and physiologically meaningful in the working-memory task.

The right target should be region-level or electrode-group-level, not a variable-length raw electrode vector. Region summaries can handle different implanted contacts across subjects and make the verification artifact easier to audit.

### Candidate C: subject-specific iEEG waveform reconstruction

This should be diagnostic only in the first Dandelion project.

It is useful to replicate a small version of the NeuroFlowNet idea or compare a simple linear/temporal CNN baseline, but this should not be the headline unless the project explicitly accepts subject-specific calibration as the claim. Waveform reconstruction is visually compelling and dangerous for exactly that reason: plausible traces can hide poor out-of-subject transfer or poor state validity.

### Candidate D: population firing or single-unit inference

This is not a first-rung target.

The unit recordings are valuable for validation and future work, but single-unit activity is sparse, subject-specific, electrode-specific, and likely too far downstream from scalp EEG for the first claim. A safer early use is to define or validate MTL state labels, not to predict individual units from scalp EEG.

## Recommended Phase 1 technical shape

### Primary evaluation

Use leave-one-subject-out as the headline evaluation. If a model has hyperparameters, tune them inside the training subjects only. Do not choose channels, frequency bands, time windows, or target thresholds using the held-out subject.

Given 9 subjects, report per-subject scores, not just means. The per-subject plot is part of the claim.

### Controls

At minimum, include:

- Label-shuffled control within training folds.
- Behavioral-only control using task variables and timing but no scalp signal.
- Timing-only control, because the task structure may create predictable temporal patterns.
- Subject identity leakage check where applicable.
- Autocorrelation/window leakage control: adjacent windows from the same trial or subject must not cross train/test boundaries in the headline result.
- Scalp artifact sanity checks: eye/muscle/probe channels or obvious non-neural features should not dominate the signal.

### Feature and model ladder

Start with compact, interpretable features:

- Band power in theta, alpha, beta, and possibly low gamma if signal quality supports it.
- Trial-phase windows tied to encoding, maintenance, and recall.
- Covariance or log-variance features across scalp channels.
- Phase-locking or coherence features only if the target definition avoids circularity.

Model ladder:

1. Regularized logistic/linear regression or elastic net.
2. Filter-bank covariance features with shrinkage LDA or ridge/logistic regression.
3. Riemannian covariance classifier/regressor as a small-data diagnostic.
4. EEGNet or a similarly compact CNN only after simple baselines are locked.
5. Foundation models only as a later optional comparison, not as the first rung.

This ladder keeps compute compatible with the local laptop GPU and makes failure interpretable.

### Statistics

Use confidence intervals and subject-level permutation tests. With 9 subjects, p-values will be unstable and should not be the only success criterion. Predeclare a minimum effect size over controls and require that the result is not carried by one subject.

### Verification artifact

For the director, build a one-subject-at-a-time verification notebook or script output that shows:

- The held-out subject.
- The scalp input window.
- The true iEEG-derived target.
- The model prediction.
- The control predictions.
- A short explanation of whether this subject supports, weakens, or contradicts the claim.

The most convincing artifact will be a small dashboard or static report over all 9 held-out folds, not a single cherry-picked trace.

## Licensing and reuse notes

The dataset is CC BY-SA 4.0. It permits commercial use, but sharing adapted material triggers attribution and ShareAlike obligations. My practical read for Phase 1 is:

- It is safe to use the dataset for analysis if attribution and license notices are preserved.
- Do not redistribute raw data in the repository.
- Treat released derived datasets, heavily transformed data, and possibly trained weights as license-sensitive until the project decides a policy.
- Public reports, figures, and reproducibility instructions should clearly cite the dataset and license.
- Code written by Dandelion can be permissively licensed, but any artifact that embeds or adapts substantial dataset content may need CC BY-SA-compatible handling.

This is an engineering risk assessment, not legal advice. The Claim Sheet should record the uncertainty rather than bury it.

For third-party code:

- NeuroFlowNet should not be reused unless its repository license is verified as commercially usable.
- LaBraM code appears MIT-licensed, but its recommended pretraining scale is far beyond this project and pretrained checkpoint/data provenance should be checked before use.
- Standard Python libraries need pinned versions and documented licenses once Phase 1 starts implementation.

## Where I agree with Claude's opening chat before reading Claude's full foundation

Based on the active chat, I agree with the main direction: coupling-signature decoding is the right frame, not naive field recovery. I also agree that leakage is the biggest methodological risk and that a low-risk first rung should probably be a deep-validated working-memory state rather than a full waveform reconstruction.

My main additions are:

- Make the first headline explicitly subject-held-out, even if it makes success harder.
- Avoid using scalp signals to define the target if scalp signals are also the predictor; if coupling is the target, define the target from intracranial or carefully separated cortical/deep components.
- Keep NeuroFlowNet as prior art and a diagnostic reference, not as the initial implementation template.
- Treat ShareAlike and model-weight release as an explicit Phase 1 policy issue.

## Open questions for Phase 1

1. What is the primary target: working-memory load, MTL band-power, MTL-cortical coupling state, or a two-stage target where load is primary and coupling validates mechanism?
2. Which MTL structures have enough coverage across subjects to support a comparable region-level target?
3. Does the Fedele scalp-hippocampal coupling preprint cited in Claude's chat have full methods available and a stable citation? I could not verify it directly during this session.
4. What artifact license will Dandelion use if derived figures or model weights are released from CC BY-SA data?
5. Should Phase 1 include a tiny subject-specific reconstruction diagnostic to contextualize NeuroFlowNet, or should it stay entirely focused on subject-held-out state decoding?

## Recommended Claim Sheet stance

Phase 1 should draft the Claim Sheet around Candidate A, with Candidate B as the planned extension if A clears its gate.

The transferable claim should be modest and auditable:

> Scalp EEG contains a subject-transferable signature of an intracranially validated MTL working-memory state in the simultaneous EEG/iEEG verbal working-memory dataset.

That claim is small enough to test honestly and large enough to matter for the long-term electrical-fMRI direction.
