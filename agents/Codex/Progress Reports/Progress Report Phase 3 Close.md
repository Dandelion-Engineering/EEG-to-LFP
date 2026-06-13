# Progress Report - Phase 3 Close

**Agent:** Codex
**Date/Time:** 2026-06-12 18:19 PDT
**Trigger:** Phase transition - Phase 3 deliverables are approved and closeable.
**For:** Randy / generalist project director

---

## The one-paragraph version

Phase 3 is now closeable. The project has all three required public artifacts: the Technical Report, the Accessible Piece, and the Reproducibility Packet. The important last blocker was not a new scientific question; it was a reproducibility standard. We needed to prove that the final result could be regenerated from a clean output tree without leaning on the existing expensive EEGNet cache. Claude recorded that full clean-room run while Codex sessions overlapped, and Codex independently confirmed the expensive EEGNet and downstream chain today before stamping approval. The regenerated dashboard matches the shipped dashboard byte-for-byte, and the final numbers still say the same thing: this first rung is a clean negative for subject-transferable scalp decoding, plus an exploratory deep-brain coupling lead that did not validate under the confirmatory gate.

## What closed today

Claude had already built the Reproducibility Packet and asked Codex to review it. In the previous Codex session I approved the packet structure and the decision not to duplicate the root `scripts/` and `utils/` folders inside the packet. That design is still correct: the repository is the reproduction unit, and copying the code into the packet would create a stale fork.

The one remaining gap was the slow default EEGNet run from a clean output tree. Earlier Codex validation had rebuilt the reader, trial metadata, montage audit, features, leave-one-subject-out folds, linear model, tangent-space Riemannian model, and MDM model, but the EEGNet stage exceeded a one-hour timeout. Claude then recorded a full clean-room run in the packet-review chat while our sessions overlapped. Today I provided the final packet stamp and independently reran the expensive EEGNet stage without the one-hour cutoff. It finished after about 98 minutes.

The clean EEGNet run reproduced the headline result:

| Quantity | Clean regenerated value | Verdict |
|---|---:|---|
| Mean signal balanced accuracy | 0.616 | same headline model |
| Mean strongest-control balanced accuracy | 0.593 | behavioral control remains strongest |
| Mean improvement over strongest control | +0.023 | below +0.075 bar |
| Subjects above strongest control | 5/9 | below 7/9 bar |
| Minimum leave-one-subject-out mean | -0.001 | fails robustness bar |
| Headline success | false | bounded negative |

After that, I regenerated the rest of the packet chain from the same clean tree: non-signal controls, behavioral-control ablation, subject statistics, MTL coverage, MTL bandpower, residual coupling, confirmatory gate, amendment evidence, and the verification dashboard.

The shipped dashboard in `deliverables/reproducibility_packet/verification_dashboard.html` is now verified against a clean end-to-end regeneration. The regenerated dashboard hash matched byte-for-byte. The regenerated subject-statistics summary also matched canonical `outputs/statistics/summary_eegnet_raw_all.json` byte-for-byte. The confirmatory gate JSON differed only because it records the scratch-tree input paths; the metric values and failed verdict matched.

## Where the science stands

The scientific result has not changed. It is now better supported operationally.

Part A is the bounded negative: with the locked common montage of 8 scalp channels, no model in the predeclared ladder clears the cross-subject success bar. EEGNet is the strongest model and the only one above the strongest non-signal control on the mean, but the effect is too small, appears in too few subjects, and collapses when subject S04 is removed.

Part B remains exploratory: the EEGNet score has a suggestive raw coupling to the recorded MTL theta-alpha signal, but the confirmatory schedule-residualized gate fails clearly. The gate result remains `gate_passed=false`, with schedule-residualized mean `+0.011`, `4/9` positive subjects, two-sided sign-flip `p=0.7461`, and min leave-one-subject-out mean `-0.010`.

That means the project leaves behind an honest map of this first rung: the current 8-channel cross-subject scalp setup is not enough, but the MTL theta-alpha coupling is a named lead for a future, better-powered project.

## Approved public artifacts

- `deliverables/technical_report/` - Technical Report source is approved by Codex. Local PDF compilation is still blocked by MiKTeX configuration before the source is processed, so the source is the approved artifact.
- `deliverables/accessible_piece/Accessible Piece.md` - Accessible Piece was approved by Codex after one precision edit.
- `deliverables/reproducibility_packet/` - Reproducibility Packet is approved by Codex after the clean EEGNet and downstream regeneration gate passed.

## What remains outside Phase 3

The main remaining issue is environmental, not scientific: MiKTeX on this machine cannot rebuild `pdflatex.fmt` because `formats.ini` is missing and the local MiKTeX lock path has permission failures. A future maintenance task can repair or replace the TeX installation and compile the Technical Report PDF, but this does not block the approved source package.

There is no reason to reopen the model ladder for this project. Additional decoders, richer channel sets, or mechanism-direct variants would be new claims or future projects, not a rescue of the original locked success bar.

## Files to start with

- `deliverables/reproducibility_packet/README.md` - best starting point for an outside reader reproducing the result.
- `deliverables/reproducibility_packet/verification_dashboard.html` - director-facing verification artifact.
- `deliverables/accessible_piece/Accessible Piece.md` - plain-language final story.
- `deliverables/technical_report/main.tex` - technical report source.
- `Claim Sheet.md` and `Accessible Claim Sheet.md` - approved project contract and Amendment 1.
