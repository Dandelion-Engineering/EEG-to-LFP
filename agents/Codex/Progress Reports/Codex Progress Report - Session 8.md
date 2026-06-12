# Codex Progress Report - Session 8

**Current Date and Time:** 2026-06-11 16:43 PDT
**Scope:** Codex Sessions 1-8
**Audience:** Randy / generalist project director

## Plain-Language Status

The project has moved from "is this first rung even well-posed?" into Phase 2 execution. The technical claim is now fixed: use cheap scalp [EEG](https://www.mayoclinic.org/tests-procedures/eeg/about/pac-20393875) to predict working-memory load on a person the model has never seen, and then check whether that surface signal is tied to real medial-temporal-lobe activity. The long-term "electrical fMRI" goal remains a north star, not a current claim; this project is testing the smallest credible first rung toward it.

So far, the decoding result is negative under the current Claim Sheet bar. The best completed scalp-only models predict working-memory load a little above chance, but they do not beat the strongest non-signal control. That matters: the project is not allowed to claim success just because a model gets a number above 0.50. It has to beat honest alternatives that use task and behavior metadata but no brain signal.

The strongest control is now understood. It is driven by `previous_trial_correct`, because the dataset task rule makes an incorrect response very likely to be followed by a low-load trial. That means the behavioral control is not an implementation leak; it is a real task-schedule signal that the current Claim Sheet predeclared as fair to beat.

The mechanism side is more promising but still incomplete. All 9 subjects have adequate medial-temporal-lobe electrode coverage, so the deep validation layer is not blocked by anatomy. A first MTL band-power probe found that the MTL theta-minus-alpha power difference changes with load in 7/9 subjects, but the current scalp tangent-decoder scores do not visibly track that intracranial summary. That is useful evidence, not a mechanism victory.

## What Codex Has Contributed

- Built the Phase 0 literature foundation and pushed the project toward a coupling-signature framing rather than claiming direct deep-field recovery from the scalp.
- Reviewed and tightened the Phase 1 Claim Sheet, especially the subject-held-out split, behavioral-control hygiene, maintenance-period target, and concrete success criteria.
- Wrote the Phase 2 controls/statistics specification before model results were interpreted.
- Implemented the controls/statistics/dashboard lane:
  - `scripts/run_control_models.py`
  - `scripts/summarize_subject_statistics.py`
  - `scripts/render_verification_dashboard.py`
- Added the behavioral-control ablation:
  - `scripts/run_behavioral_control_ablation.py`
- Added the first mechanism scaffold:
  - `utils.nix_io.load_ieeg_epochs(...)`
  - `utils/mechanism.py`
  - `scripts/run_mtl_bandpower_probe.py`

## Result Snapshot

Current completed decoding rungs:

| Rung | Mean signal balanced accuracy | Mean strongest control | Mean improvement | Subjects above control |
| --- | ---: | ---: | ---: | ---: |
| Logistic all features | 0.560 | 0.593 | -0.033 | 3/9 |
| Riemannian tangent covariance | 0.558 | 0.593 | -0.036 | 3/9 |

Behavioral-control ablation:

| Control component | Mean balanced accuracy |
| --- | ---: |
| Response time only | 0.500 |
| Correctness + match/mismatch | 0.500 |
| Previous-trial correctness only | 0.596 |
| Trial/session controls | 0.500 |
| Full behavioral control | 0.593 |

First MTL mechanism probe, using the completed tangent rung:

| Metric | Mean | Subject pattern |
| --- | ---: | --- |
| MTL theta load effect | 0.120 z | 5/9 positive |
| MTL alpha load effect | 0.025 z | 5/9 positive |
| MTL theta-minus-alpha load effect | 0.143 z | 7/9 positive, p = 0.0156 |
| Tangent score vs MTL theta | -0.011 correlation | near zero |
| Tangent score vs MTL alpha | -0.018 correlation | near zero |

## What This Means

The current scalp decoder has not cleared the evidence bar. That is not a project failure yet, because the predeclared EEGNet rung is still pending, but the linear/Riemannian ladder is exhausted.

The intracranial MTL layer contains load-relevant structure worth following. The theta-minus-alpha result is the strongest mechanism hint so far. However, the current scalp decoder does not appear to be using that MTL structure. The next honest question is whether EEGNet changes that or whether the project needs an amendment discussion after the model ladder and fuller mechanism analysis are both available.

## Main Risks

- **Overclaim risk:** The project must not turn the MTL theta-minus-alpha probe into a full deep-readout claim. It is a scaffold, not the final coupling analysis.
- **Model-ladder incompleteness:** EEGNet is not yet represented in completed outputs.
- **Git closeout blocker:** Codex still cannot write `.git/index.lock`, so Codex changes remain unstaged and uncommitted in this environment.
- **Small-n constraint:** There are only 9 subjects, so subject-level evidence is the correct bar; trial-level volume cannot substitute for subject generalization.

## Next Steps

1. Run the bounded EEGNet rung or consume Claude's EEGNet outputs when available.
2. Pass EEGNet through `run_control_models.py`, `summarize_subject_statistics.py`, and the dashboard renderer.
3. Rerun `run_mtl_bandpower_probe.py` against EEGNet scores.
4. Extend the mechanism layer beyond band power toward the fuller theta-alpha/coupling analysis named in the Claim Sheet.
5. If EEGNet also fails and mechanism evidence remains meaningful, open an amendment discussion rather than editing the Claim Sheet unilaterally.
