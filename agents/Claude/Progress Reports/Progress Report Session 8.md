# Progress Report — Session 8 (Cadence)

**Agent:** Claude
**Date/Time:** 2026-06-12 08:20 PST
**Trigger:** Regular cadence — my 8th session.
**For:** Randy (the director). Written to be read start to finish without looking anything up.

---

## The one-paragraph version

Since my last report (when we finished signing the project's plan), we built and ran the whole "ladder" of models that read working-memory load from scalp EEG, and we now have a clear answer to the first half of the project: **no model we tried can read memory load from 8 scalp channels well enough to beat a fair baseline in a way that transfers from one person to the next.** That sounds like a letdown, but it's a clean, honest result — we mapped exactly where the wall is. The genuinely exciting part is the *second* half: the best model's output has started to **track the real deep-brain memory signal** recorded from electrodes inside the brain — the first positive evidence that the scalp carries information about the deep structures we ultimately care about. That flips the project's center of gravity, and I've proposed a formal change of plan to my collaborator Codex to chase the coupling result rather than keep pushing on the decoding number.

## A little background you'll want for the rest of this report

Three ideas make everything below make sense. I'll keep each short.

**1. What "working-memory load" is, and how the task measures it.** Working memory is the small amount of information you can actively hold "in mind" for a few seconds — like keeping a phone number in your head while you dial. In this dataset, people were shown a few letters, asked to hold them silently for about 3 seconds, and then tested. "Load" just means *how many* letters they were holding (we compare a low-load case to a high-load case). More load = the brain is working harder to maintain more items. ([Working memory — overview](https://www.ncbi.nlm.nih.gov/books/NBK545131/))

**2. Scalp EEG vs. electrodes inside the brain.** EEG (electroencephalography) reads brain activity from sensors resting on the scalp — cheap, painless, and what makes this project's long-term vision affordable. But the skull blurs and weakens the signal, so scalp EEG sees a smeared-together summary. These particular patients (epilepsy patients awaiting surgery) also had electrodes placed *inside* the brain for medical reasons, recording the deep memory hub directly. That's the rare and valuable thing: we get the cheap outside view and the gold-standard inside view **at the same moment**, so we can check the outside against the inside. ([Intracranial EEG, plain overview](https://www.ninds.nih.gov/health-information/disorders/epilepsy-and-seizures))

**3. The honesty machinery: baselines, "leave-one-person-out," and pre-set success bars.** Three guardrails run through everything:
   - A **baseline** is a "boring" competitor that's only allowed to use non-brain facts (like how fast the person answered). If our brain model can't beat the boring baseline, the brain signal isn't earning its keep.
   - **Leave-one-person-out** means we train the model on 8 people and test it on the 9th — someone it has never seen. This is the hard, honest test of whether a signal is *general* rather than a quirk of one person. ([Cross-validation, plain explanation](https://scikit-learn.org/stable/modules/cross_validation.html))
   - A **pre-set success bar** is the passing grade, written down *before* we look at any result so we can't move the goalposts. Ours: beat the baseline by at least +0.075, in at least 7 of 9 people, and survive the removal of any single person (so one lucky person can't carry the result).

## Where the project stands right now

We are at the **end of the decoding investigation and the start of a pivot.** The first half of the project — "can a model read load from the scalp?" — is answered (no, not to our bar). The second half — "does the scalp signal actually reflect the deep brain?" — just produced its first encouraging sign. I've proposed re-centering the project on that second half. Codex hasn't yet weighed in on the proposal, so nothing in the official plan has changed; that's the immediate next step.

## What's been done since the last report

After we signed the plan, we built and tested a **ladder of four model types**, each more powerful than the last, all judged by the exact same honest test. Here's how each one did at reading load from the scalp (0.50 is a coin-flip; the fair baseline to beat is 0.593):

| Model (rung) | What it does, in plain terms | Score |
|---|---|---|
| Linear | Draws a straight dividing line through simple brain-wave power features | 0.560 |
| Covariance | Uses how channels move *together*, not just their individual power | 0.559 |
| Riemannian | A more sophisticated geometry for comparing those co-movement patterns | 0.558 / 0.533 |
| **EEGNet** | A small **neural network** that learns its own patterns from the raw waveform | **0.616** |
| *Fair baseline* | *Boring competitor using only non-brain facts* | *0.593* |

The first three all came in *below* the baseline. EEGNet — a compact neural network ([the standard EEGNet design](https://doi.org/10.1088/1741-2552/aace8c)) — was the first to edge *above* it (0.616 vs 0.593). For a moment that looked like a breakthrough. But our pre-set robustness check caught the catch: **the entire advantage came from one single person.** Remove that person and the average improvement drops to essentially zero. Only 5 of the 9 people improved at all (we required 7), and the improvement margin was +0.023 (we required +0.075). So EEGNet *fails the bar* — and it fails it for exactly the reason our robustness rule was designed to expose. That rule did its job: it stopped a one-person fluke from being reported as a group finding.

**The bottom line on the decoding half:** we tried every model type we committed to, and none reads working-memory load from these 8 scalp channels well enough to transfer across people. That is a real, mappable boundary — valuable precisely because we can state it with confidence rather than hand-wave it.

## What was found that we did NOT expect

Two things, and the second is the important one.

**Unexpected #1 — the neural network beat the baseline on average, but only because of one person.** I had predicted EEGNet wouldn't beat the baseline at all. It did, on the average — then the robustness check revealed the average was propped up by a single subject. So my prediction was both wrong (on the average) and right (on the conclusion). The lesson is that the average alone would have misled us; the per-person robustness rule is what kept us honest.

**Unexpected #2 — the better the scalp decoder, the more it "sees" the deep brain.** This is the finding that changes the project. Separately from the decoding contest, we measure the *real* deep-brain memory signal from the inside electrodes (a specific brain-wave pattern — a theta-vs-alpha rhythm difference in the memory hub — that genuinely shifts with memory load: present in 7 of 9 people, statistically solid). Then we ask: does our scalp model's output *track* that deep signal? With the older linear models, the answer was flatly no — the relationship was essentially zero. With EEGNet's output, the relationship **flipped positive across the board**, showing up in 7 of 9 people and landing right at the edge of statistical significance. In plain terms: **the model that reads the scalp a little better also tracks the deep brain a little better.** It is not yet proven — the effect is modest and sits right on the significance line — but the *direction* is consistent and it is the first real thread connecting the cheap scalp signal to the deep memory structures. That is, ultimately, the whole point of the long-term vision ("electrical fMRI" — using cheap EEG plus AI to glimpse deep-brain activity that today needs a million-dollar scanner).

## What's working / what isn't

- **Working:** the entire analysis pipeline (data reader, feature builder, all four model rungs, the scoring and statistics harness, and the deep-brain coupling probe) runs end to end. The laptop's disk problem from last session is fully resolved (you cleared ~430 GB — thank you; that's what unblocked this whole session).
- **Not working / not yet:** the original headline goal — a scalp decoder that beats the baseline across people — is not achievable from this montage, and we've now confirmed that across every model we planned to try. That's a closed door, cleanly documented.
- **In motion (not a problem):** the pivot itself. I've proposed re-centering on the deep-brain coupling result; Codex needs to agree before the official plan changes. Until then I haven't altered the contract.

## What the next stretch of work looks like

1. **Settle the change of plan with Codex.** I've proposed splitting the project's result into an honest two-part story: (A) a clean "here's where the wall is" boundary result for the decoding half, and (B) a new positive center — "the scalp signature is coupled to recorded deep-brain activity." He approves, pushes back, or refines; we reach agreement before anything moves.
2. **Build a proper confirmatory test for the coupling.** The encouraging coupling number came from an exploratory look, which can flatter itself. The disciplined next step is to fix the exact measurement in advance and re-test it cleanly, so the result either holds up as a genuine finding or is honestly labeled "suggestive but underpowered." I'd rather under-claim and be right.
3. **Keep building your verification dashboard** so that, whatever the final result, you can see it with your own eyes — per person, side by side: what the model saw, what it guessed, and the real deep recording it was (or wasn't) tracking.

## Where the files are

- **Your plain-language plan:** `Accessible Claim Sheet.md` (project root) — the project's contract in plain English. *(You approved this in your last check-in — thank you.)*
- **The decoding verdict and my change-of-plan proposal:** `chats/Claude-Codex/Riemannian Ladder Verdict/` — the live conversation where the pivot is being decided.
- **Your requests log:** `director_requests.md` (project root) — both open requests are now resolved (disk freed; Claim Sheet approved).
- **The per-session detail for this session:** `agents/Claude/Session Summaries/HumanReport8.md`.
