# Claude Session 5 — Human Report

**Current Date and Time:** 2026-06-11 11:45 PDT

## Summary

This session turned the validated data layer into a working decoding pipeline. The one
decision that was blocking the first model — which scalp channels the cross-subject
analysis runs on — was settled by Codex at the start of this session, which unblocked
everything. I then built the feature-extraction layer, the leave-one-subject-out
evaluation folds, and the first signal model, and ran it end to end. We now have our
first real number: scalp EEG predicts working-memory load across subjects at roughly
0.56 balanced accuracy from the maintenance period, with the result surviving the
removal of the ear-reference channels. That is a first rung on a pre-registered model
ladder, not the final answer, but it is a genuine, leakage-controlled result handed off
cleanly to Codex's controls lane.

### What "the project" is doing right now, in plain terms

We are testing whether cheap scalp EEG carries a usable trace of deep-brain (medial
temporal lobe) working-memory activity. The specific, measurable first claim is: can a
model trained on eight people predict how many items a *ninth, never-seen* person is
holding in memory (a lot = 6 or 8 letters, vs. a few = 4), using only the scalp signal
during the "hold it in mind" period of the task? "Never-seen person" is the hard part —
that is the leave-one-subject-out (LOSO) test, and it is what would make the result
actually useful rather than a per-person curiosity.

## What was accomplished

1. **Read the full project context and Codex's Session 5 handoff.** Codex reviewed my
   Session 4 trial-count audit and montage finding and **locked the configuration**: the
   pre-registered success bar (a +0.075 balanced-accuracy improvement over the strongest
   non-signal control) stands, and the headline cross-subject run uses only the 8 scalp
   channels present in all 9 subjects (A1, A2, C3, C4, F3, F4, O1, O2), with no
   fabricated/padded channels. Because A1/A2 are ear-reference channels, he required a
   predeclared "brain-only" sensitivity check that drops them.

2. **Built the feature-extraction layer** (`utils/features.py` + `scripts/build_features.py`).
   For each trial's maintenance window it computes two families of scalp-only features:
   - **Band power** — how much energy sits in each classic EEG frequency band (delta,
     theta, alpha, beta, gamma) at each channel.
   - **Covariance (tangent-space)** — how the channels co-vary with each other in each
     band, encoded in the standard "Riemannian tangent space" form that machine-learning
     classifiers handle well. This captures *spatial pattern* information that plain band
     power throws away.
   A careful detail: filtering is done on the full 8-second epoch and the 3-second
   maintenance window is cut *afterward*, so no filtering artifact at the window edge can
   sneak in and create a fake signal. The output is a single bundle file (1,683 trials ×
   220 features) plus metadata, with the 144 artifact-flagged trials dropped and listed
   explicitly (no silent exclusions). The 1,683 count matches the audit exactly.

3. **Built and validated the LOSO folds** (`scripts/make_loso_splits.py`). Nine folds,
   one per held-out subject. The script checks the two ways this kind of evaluation
   usually leaks — a subject appearing in both training and test, or a held-out subject
   having only one class — and both guards pass.

4. **Built the first signal model** (`scripts/run_load_decoder.py`) — a regularized
   logistic-regression / LDA decoder, rung 1 of the planned model ladder. The discipline
   that makes the number trustworthy: the held-out subject is touched exactly once. All
   standardization and tuning happen on the training subjects only; the held-out person
   is scored a single time with the frozen model. Results (balanced accuracy, where 0.50
   = chance), signal side only:

   | Configuration | Mean LOSO balanced accuracy |
   |---|---|
   | logistic, band power, 8-ch | 0.512 |
   | logistic, covariance, 8-ch | 0.559 |
   | logistic, all features, 8-ch (**headline candidate**) | **0.560** (8/9 subjects > 0.50) |
   | LDA, all features, 8-ch | 0.552 |
   | logistic, all features, **brain-only (A1/A2 removed)** | 0.557 |

5. **Handed everything off to Codex and concluded the coordination chat.** The
   "Phase 2 Controls Interface" chat reached its purpose — settle the montage/bar and
   deliver the interface artifacts — so I posted the full handoff and concluded it
   (`...Concluded.md` + `Summary.md`). Codex now implements the control models on the
   exact same folds.

## What was found that was not expected

- **Spatial covariance carries the signal; band power alone barely does.** Plain
  band-power decoding sat at 0.512 (essentially chance), but adding the channel-to-channel
  covariance structure lifted it to 0.56. This is consistent with the working hypothesis:
  a deep-brain contribution to the scalp would show up as a *distributed spatial pattern*
  across electrodes, not as a bump in one channel's band power. It is encouraging that the
  feature family motivated by the mechanism is the one that helps.

- **The result is not an artifact of the ear-reference channels.** The brain-only check
  (0.557) was essentially identical to the full 8-channel result (0.560). If the
  "signal" had really been driven by A1/A2 reference quirks, dropping them would have
  collapsed the result. It did not. Codex's predeclared sanity check passes on rung 1.

## What is working / what isn't

- **Working:** the full pipeline runs end to end on real data, the leakage guards hold,
  the counts reconcile with the audit, and we have a reproducible first number with an
  honest sensitivity check already attached.
- **Not yet there:** 0.56 is modest. The claim is not "0.56 accuracy" — it is
  "improvement over the strongest non-signal control of at least +0.075." That subtraction
  is Codex's next step (he computes how well behavior/timing/shuffled-label baselines do
  on the same folds). On rung 1 the margin may well land under +0.075; that is *expected
  headroom* for the higher rungs of the pre-registered model ladder (filter-bank
  covariance + shrinkage, then Riemannian geometry, then a compact neural network), not a
  failure. We deliberately did not stop at one model.

## Important decisions and reasoning

- **Adopted Codex's locked montage/bar without re-litigating it.** He concurred with my
  recommended Option 1; the decision is sound and pre-registration discipline says we
  build, not re-argue. No Claim Sheet amendment is needed — this was a Phase 2 config
  decision, and the Claim Sheet already specifies LOSO, balanced accuracy, and the +0.075
  bar.
- **Included both feature families in the bundle now,** even though rung 1 mainly needs
  band power, so Codex's controls and my later covariance/Riemannian rungs run on the same
  artifact without a rebuild. I also saved the raw shrunk covariance matrices for the
  Riemannian rung. This is cheap (the bundle is small) and avoids re-deriving features.
- **Treated covariance via tangent-space vectorization** (the established Barachant 2012
  method) rather than inventing a representation — it gives a flat, classifier-ready form
  now and the correct geometric object for the Riemannian rung later. Added to
  `references.md` with a verified link.

## Files created or updated

- Created `utils/features.py` — band-power + tangent-space covariance feature extraction.
- Created `scripts/build_features.py` — builds the feature bundle from all sessions.
- Created `scripts/make_loso_splits.py` — emits + validates the 9 LOSO folds.
- Created `scripts/run_load_decoder.py` — rung-1 logistic/LDA signal decoder.
- Created (local, gitignored) `outputs/features/` (feature_bundle.npz, feature_metadata.{parquet,csv},
  exclusions.csv, feature_names.json, loso_folds.json, loso_fold_assignment.csv) and
  `outputs/decoding/` (predictions_*, subject_scores_*, summary_*.json for each config).
- Appended handoff to and concluded `chats/Claude-Codex/Phase 2 Controls Interface/`
  (renamed to `...Concluded.md`, added `Summary.md`).
- Updated `agents/Claude/references.md` (Barachant 2012, Riemannian covariance method).
- Updated `agents/Claude/README.md` and rewrote `agents/Claude/Summary of Only Necessary Context.md`.

## Next steps / pending actions

- **Codex (next):** implement the control models (label-shuffle, behavioral-only,
  timing-only, subject-identity) on the delivered folds/bundle, then compute per-subject
  improvement and the subject-level statistics that decide the +0.075 test.
- **Me (next session):** climb the model ladder — filter-bank covariance + shrinkage,
  then Riemannian geometry — to see whether the signal margin over controls grows past
  the bar. Begin the mechanism layer's coverage audit (which subjects have adequate MTL
  electrode coverage) using the lazy iEEG/electrode reader.
- **Process note:** my next cadence progress report is due at my **Session 8** (this was
  Session 5). No phase transition or amendment occurred this session, so no progress
  report was triggered now.

## Git note

I committed this session's work and — as in prior sessions — also staged Codex's
uncommitted Session 5 working-tree changes (his report notes a `.git/index.lock`
permission error blocked his own commit). The push captures both.
