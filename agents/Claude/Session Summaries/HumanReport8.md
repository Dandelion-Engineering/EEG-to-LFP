# Claude — Human Report 8

**Current Date and Time:** 2026-06-12 08:10 PST

## Summary

This was the session the project had been waiting on. Last session I built the final model on our decoding "ladder" — EEGNet, a small neural network — but couldn't run it because the laptop was out of disk space. **Randy freed the disk (C: went from ~3 GB to ~430 GB free), so this session I ran it, scored it, and ran the brain-coupling check.** The decoding ladder is now complete, and the result is a clear, honest turning point for the project. Codex ran a session in parallel and approved the re-point (with a sharpening I adopted), so **Amendment 1 is now ratified** — the project's plan officially changed this session. (A separate, focused report — `Progress Report Amendment 1 ...` — covers that change in detail.)

A one-paragraph reminder of what we're doing: we're testing whether cheap scalp EEG (electrodes on the outside of the head) carries a usable, person-to-person-transferable signature of working-memory "load" — how many items someone is holding in mind — and we check our answers against gold-standard electrodes recorded *inside* the brain (in the medial temporal lobe, the brain's memory hub). We test this by climbing a ladder of progressively more powerful models. If even the best model can't read load from the scalp well enough to beat a fair baseline, that's a real and publishable boundary; and separately, we can ask whether the scalp signature — even when weak — actually tracks the deep-brain activity, which is the more interesting scientific question.

### The headline result: the decoding ladder is exhausted, but EEGNet surprised us twice

**EEGNet is the best rung we've run — and the first to beat the baseline on average — but it still fails our success bar, and it fails it in a way that's actually informative.**

The numbers (mean across the 9 held-out people, where 0.50 is pure chance):

| Model rung | Score |
|---|---|
| Rung 1 — linear | 0.560 |
| Rung 1 — covariance | 0.559 |
| Rung 2 — Riemannian (tangent) | 0.558 |
| Rung 3 — Riemannian (MDM) | 0.533 |
| **Rung 4 — EEGNet** | **0.616** |
| *Strongest fair baseline (behavioral-only)* | *0.593* |

**Surprise #1:** Rungs 1–3 all landed below the 0.593 baseline. EEGNet is the first to clear it on average (0.616). So learning patterns directly from the raw brain-wave shape *does* squeeze out a little more than the hand-built features did. My prediction last session ("EEGNet probably won't beat 0.593 either") was wrong on the average.

**But it does not pass our pre-registered success bar, and here's the honest reason.** Our success bar (set before we saw any results, exactly so we couldn't move the goalposts) required three things: an average improvement of at least +0.075 over the baseline, at least 7 of 9 people showing improvement, and — crucially — *robustness*: the result can't fall apart if you remove any single person. EEGNet's average improvement was only **+0.023**, only **5 of 9** people improved, and **the entire positive average rests on one person** (subject S04, who improved by +0.218; the next best was +0.045). Remove S04 and the average improvement collapses to **−0.001** — essentially nothing. A 95%-confidence range on the improvement runs from −0.022 to +0.081, which includes zero. That robustness check is precisely the trap-detector we built in advance, and it caught a one-person fluke masquerading as a group effect.

**Verdict:** we have now tried every model type we pre-committed to — linear, covariance, curved-geometry (Riemannian), and a neural network — and none of them can read working-memory load from this 8-channel scalp montage well enough to beat the fair baseline in a way that transfers across people. That's not a failure of effort; it's a clean, well-characterized *boundary*. We can state with confidence where the wall is.

### Surprise #2: the better decoder actually starts to "see" the deep brain

This is the part that matters most. Codex's "mechanism" tool measures the real deep-brain load signature from the in-brain electrodes and asks whether our scalp decoder's output *tracks* it. Last session, with the older (linear) decoder, the answer was a flat no — the correlation was essentially zero (−0.01). This session, with EEGNet's output:

| Coupling to deep-brain signal | Old (linear) decoder | **EEGNet decoder** |
|---|---|---|
| vs. MTL theta rhythm | −0.011 | **+0.078** |
| vs. MTL theta-minus-alpha | −0.015 | **+0.068 (7 of 9 people, p ≈ 0.05)** |

The coupling flipped from zero/negative to **positive across the board**, and the strongest version (theta-minus-alpha) now shows up in 7 of 9 people, sitting right at the edge of statistical significance (p ≈ 0.0508). I want to be careful here: this is **not yet proven** — the correlations are modest and the p-value is borderline, and it came from an exploratory probe. But the *direction* is consistent and meaningful: **the better our scalp decoder gets, the more its output tracks genuine deep-brain memory activity.** That is the first positive evidence this project has produced that the scalp signature has a real relationship to the deep structures we ultimately care about — which is, after all, the entire long-term point ("electrical fMRI").

### The decision this forced — and the amendment we ratified

These two results together put us exactly where Codex and I had flagged we might end up. The decoding question, as originally scoped (+0.075 transferable improvement from this montage), is answered — the answer is "no, not from 8 scalp channels across people." The coupling result is where the live scientific signal is. I proposed a formal **amendment** to re-point the project, and Codex — running a session in parallel — approved it with one important sharpening that I adopted in full. **Amendment 1 is ratified.**

The re-pointed claim is now two-part:
- **Part A — the clean negative boundary:** rigorously document that no model class in our ladder beats the baseline across people — an honest, publishable "here's where the wall is" result.
- **Part B — the exploratory coupling lead:** the scalp decoder's output shows a *suggestive* coupling to deep-brain (MTL) activity — but, per Codex's sharpening, **explicitly not a validated deep readout.** His residualization test (which I reproduced exactly) showed the raw coupling (0.068, 7/9 people) mostly dissolves once you control for task structure — dropping to 0.011 after removing schedule effects. At 9 people the dataset can't separate "a real faint deep signal" from "a shared task-difficulty by-product," so we report it as a promising lead to test with more data, not a discovery. His narrower wording is more defensible than my original, and I took it wholesale.

Crucially, the amendment **did not lower the original passing grade** — the bar stayed fixed, was tested, and wasn't met. Both outcomes (a "clean failure" and an "inconclusive mechanism") were pre-declared as named possibilities before we ran anything; the amendment just records which came true. I drafted the amendment in both the technical Claim Sheet and your plain-language `Accessible Claim Sheet.md` (kept in sync), and left the chat open only for Codex's final read of my exact wording.

### Challenges and how I handled them

- **A path-mangling bug in my first run command.** My first launch failed instantly because the Windows backslashes in the file path got eaten by the shell (it tried to open a file literally named `outputsfeaturesfeature_bundle.npz`). Easy fix — switched to forward slashes — but worth recording. The gradient check had already re-passed (max error 4.7e-6) before that failure, so the model itself was confirmed sound on this machine before the real run.
- **The runs are genuinely slow.** Training a neural network in pure NumPy (no GPU library, by necessity — the disk still can't host PyTorch comfortably and the network is tiny anyway) across all 9 leave-one-person-out folds took ~2.2 hours for the headline and ~1.1 hours for the brain-only check. Both completed cleanly. The brain-only result (0.623, essentially equal to the all-channel 0.616) confirms the EEGNet signal isn't an artifact of the ear-reference electrodes — the predeclared reference check passes on rung 4, as it did on every earlier rung.

### What is working / not working

- **Working:** the full decoding ladder (now complete through rung 4); the scoring/statistics harness; Codex's mechanism probe and his new residualization probe; the EEGNet implementation (verified correct, now run end-to-end on both channel sets). The blocker from last session is fully cleared, and the amendment is ratified.
- **No open problems.** The project has a complete, concludable result. The only thing "in motion" is Codex's final read of my exact amendment wording (substance fully agreed) and his one prospective confirmatory coupling test.

### Files created or updated

- **Created** `outputs/decoding/predictions_eegnet_raw_all.csv`, `outputs/decoding/subject_scores_eegnet_raw_all.csv` — EEGNet rung-4 results *(gitignored outputs)*.
- **Created** `outputs/controls/control_*_eegnet_raw_all.*`, `outputs/statistics/*_eegnet_raw_all.*`, `outputs/mechanism/mtl_bandpower_*_eegnet_raw_all.*` — scoring, success-bar statistics, and EEGNet↔MTL coupling *(gitignored outputs)*.
- **Created** `outputs/decoding/predictions_eegnet_raw_brain.csv` + `subject_scores_eegnet_raw_brain.csv`, and `outputs/mechanism/mtl_residual_coupling_*_eegnet_raw_all.*` *(gitignored outputs; the residual probe is Codex's script, which I reproduced)*.
- **Amended** `Claim Sheet.md` — Amendment 1 in the Amendment log; Status updated to "Phase 2, Amendment 1 ratified."
- **Amended** `Accessible Claim Sheet.md` — matching plain-language Amendment 1 section (kept in sync, same session).
- **Updated** `chats/Claude-Codex/Riemannian Ladder Verdict/Riemannian Ladder Verdict - Active.md` — posted the complete decoding verdict, the coupling result, the brain-only number, my reproduction of Codex's residualization, and my acceptance of his narrowing; chat kept **open** only for his final read of the amendment wording.
- **Updated** `chats/Claude-Codex-Human/Some Updates/Some Updates - Active.md` — acknowledged Randy's three updates (disk freed, Claim Sheet approved, new git protocol).
- **Updated** `director_requests.md` — closed Request 1 (Claim Sheet approved) and Request 2 (disk freed) with agent notes.
- **Created** `agents/Claude/Progress Reports/Progress Report Session 8.md` — my first cadence progress report (full results background).
- **Created** `agents/Claude/Progress Reports/Progress Report Amendment 1 Decoding-to-Coupling Repoint.md` — the amendment-trigger report.
- **Updated** `agents/Claude/README.md`, `agents/Claude/references.md` (added the EEGNet/Lawhern 2018 citation), and `agents/Claude/Summary of Only Necessary Context.md`.

### Next steps / pending actions

1. **Codex's final read** of the exact amendment wording (substance fully agreed; any tweaks propagate forward) and conclusion of the `Riemannian Ladder Verdict` chat with its `Summary.md`.
2. **Build Part B's confirmatory coupling test** (Codex's mechanism lane; I feed decoder scores in) — a pre-registered test that fixes the band/metric a priori *and requires the coupling to survive residualization*, so it's no longer a max-over-a-family exploratory number.
3. **Likely move to Phase 3 (deliverables)** after that — the Technical Report, Accessible Piece, and Reproducibility Packet, since the project now has a complete, concludable result.
