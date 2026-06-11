# Accessible Claim Sheet — Reading Deep-Brain Memory Activity from Scalp EEG

**Project:** Dandelion Collaboration Station — EEG to LFP
**Companion to:** `Claim Sheet.md` (the technical contract). This document carries the *same* commitments in plain language.
**Written by:** Claude (Session 3, 2026-06-11). **Status:** Phase 1 closed; this is the director's reference companion.

> **What this document is.** The technical Claim Sheet is the contract the agents work against, and it's written in the language of the people doing the engineering — so it gets dense. This is the same contract, same promises, written for you, Randy. If anything here and the technical sheet ever disagree, that's a defect and we fix it the same session. You should be able to read this top to bottom and come away knowing exactly what we've committed to — without opening the technical sheet alongside it.

---

## The one-paragraph version

When you try to remember a phone number for a few seconds, deep structures near the center of your brain — especially a region called the **medial temporal lobe (MTL)**, the brain's memory hub — light up with electrical activity. That activity is normally invisible to a cheap sensor on the scalp: the skull blurs and buries it. But the deep memory regions don't work in isolation — they "talk to" the outer surface of the brain (the cortex) in a rhythmic, coordinated way, and *that* conversation does leave a faint trace on the scalp. **Our question for this first project: can an AI model, given only scalp EEG, tell how hard your memory is working right now — on a person it has never seen before — and can we prove that the signal it's using is genuinely the deep memory activity, not some unrelated shortcut?** We can check the answer because we have a rare dataset where scalp recordings and deep-brain recordings were captured *from the same person at the same instant*. That gives us ground truth to grade ourselves against.

---

## Why this matters (the north star)

The long-term dream — many projects away — is what Randy calls **"electrical fMRI."** [fMRI](https://www.nibib.nih.gov/science-education/science-topics/magnetic-resonance-imaging-mri) is the big-magnet brain scanner that produces those colorful maps of brain activity. It's powerful but expensive, immobile, and out of reach for almost everyone. [EEG](https://www.mayoclinic.org/tests-procedures/eeg/about/pac-20393875), by contrast, is cheap, wearable, and already in drugstores in toy form. If AI could squeeze even a *coarse* picture of deep-brain activity out of cheap scalp EEG, that would be a genuinely affordable window into the brain — exactly the kind of thing Dandelion exists to build.

That dream is too big for one project and far more than our current resources can reach. **This project is the first rung of the ladder**: the smallest honest claim that makes real, checkable progress toward it. We're not trying to reconstruct a full deep-brain movie. We're trying to prove the *first* useful piece of deep information survives the trip to the scalp and can be read by a model — and to build the reusable tooling (data readers, evaluation harness, verification dashboard) that every harder rung will stand on.

---

## The substrate — what we're working with (Slots 1, 10)

We use one open, public dataset: **Boran et al. (2020)** ([G-Node DOI](https://doi.gin.g-node.org/10.12751/g-node.d76994/)). Nine epilepsy patients — who already had electrodes implanted deep in their brains for clinical reasons — agreed to also wear a scalp EEG cap while they did a memory task. So for each person we have, *simultaneously*:

- **Scalp EEG** — the cheap signal, recorded from outside the head. This is our model's only input.
- **Intracranial recordings (iEEG / LFP)** — electrodes *inside* the brain, near the memory hub. This is the deep "ground truth" we get to check against. ("[LFP](https://en.wikipedia.org/wiki/Local_field_potential)" = local field potential, the pooled electrical hum of many nearby neurons.)
- **Single-neuron activity** — the firing of 1,526 individual memory-region neurons.

The memory task is a **modified [Sternberg task](https://en.wikipedia.org/wiki/Sternberg_task)**: the person is shown a set of letters to hold in mind (the "load" — 4, 6, or 8 letters), waits through a blank pause (the **maintenance period**, where they're just *holding* the memory), then is shown one letter and answers whether it was in the set. The number of letters they're juggling is the "working-memory load" — that's the thing our model tries to read.

**Simultaneity is the whole point.** Because the cheap signal and the deep signal come from the same brain at the same moment, "guess the deep activity from the scalp" stops being speculation and becomes a measurement we can grade.

**Our hardware:** a single consumer laptop (RTX 4070 laptop GPU, 8 GB of graphics memory, 16 GB RAM). This is deliberately modest — the affordable mission means whatever we build has to run on hardware ordinary people own. The closest prior work used a bigger 16 GB card; fitting in 8 GB is itself one of our differentiators.

---

## The problem, stated honestly (Slot 2)

The textbook view is that deep MTL activity is essentially invisible to scalp EEG. The skull conducts electricity about 80× worse than brain tissue, deep electrical fields are faint and geometrically smeared by the time they reach the surface, and working backward from scalp readings to a deep source is a notoriously [ill-posed problem](https://en.wikipedia.org/wiki/Inverse_problem) (many different deep patterns could produce the same surface reading).

**But** — and this is the opening — the deep memory regions *synchronize* with the cortex during memory tasks, in a specific rhythmic way (load-dependent **theta–alpha coupling**, more on that below), and prior work has shown that this coupling *does* reach the scalp. So the deep activity may leave an indirect fingerprint up top even when the deep field itself can't be seen directly. We're testing whether AI can read that fingerprint.

A note on the rhythms, since they recur: brain electrical activity comes in frequency bands, like notes. **[Theta](https://en.wikipedia.org/wiki/Theta_wave)** (~4–8 cycles/sec) and **alpha** (~8–12 cycles/sec) are two of them, and both are heavily involved in memory. "Theta–alpha coupling" means these rhythms rise, fall, and lock together in a coordinated way that changes with how hard memory is working — that coordinated pattern is the deep signature we're chasing.

---

## The claim — what we'd be able to say if this works (Slot 3)

In one sentence:

> **Scalp EEG carries a fingerprint of deep memory activity that transfers across people: given only scalp EEG from a person it was never trained on, an AI can tell how hard that person's working memory is loaded — better than fair comparison baselines — and we can show the signal it's using is genuinely tied to the deep memory-region activity recorded inside the brain, not an unrelated shortcut.**

This has **two halves**, and we keep them strictly separate so we never overclaim:

- **Half A — Decoding (the headline):** scalp EEG alone predicts memory load, on a held-out person, above strong baselines.
- **Half B — Mechanism (what makes it *deep*):** the signal the model relies on is provably linked to the real deep memory activity — proving we're reading the brain's memory hub indirectly, not just picking up generic "the task is hard now" cues from the cortex's surface.

Getting Half A but not Half B is a real, partial result — and we report it as exactly that, never dressed up as the full claim (see Failure/Inconclusive below).

---

## How we'll test it (Slots 5, 7) — and the one idea that matters most

The single most important design choice, because it's where projects like this usually fool themselves:

**Leave-One-Subject-Out (LOSO) testing.** Imagine nine patients. We train the AI on eight of them, then test it on the ninth — a person it has *never* seen. We do this nine times, leaving each person out once. ([This is a standard rigorous form of "cross-validation."](https://en.wikipedia.org/wiki/Cross-validation_(statistics))) Why it's the headline: it's easy to build a model that works on people it's already studied — that's like grading a student on questions they saw during study. The honest, useful, hard test is whether the signal **transfers to a stranger**. Every choice the model makes is locked in using only the training people; the held-out person is touched exactly once, for the final grade. This is what makes the result mean something for a future where you'd put the cap on someone new.

**What we predict, and when.** We read the load specifically during the **maintenance period** — the pause where the person is just *holding* the letters in mind. We chose this on purpose: if we read it during the moment the letters first appear, the model could cheat by reacting to the *sight* of more letters on the screen, rather than the *memory* itself. The maintenance window has no new stimulus — so a signal there is genuinely about the held memory.

**The specific, pre-committed target:** binary **high-vs-low load** — was the person holding **4 letters (low)** or **6–8 letters (high)?** Simple, clean, and easy for you to audit. (We also run finer versions — 3-way, and a continuous version — but those are secondary; the headline is the binary one.)

**The baselines we have to beat ("controls").** A number "above chance" can lie — the model might be reading something boring rather than the brain. So we pre-commit to beating several honest comparisons:
- **Label-shuffle:** scramble the answers and confirm the model can no longer "predict" them (proves it isn't just memorizing noise).
- **Behavioral-only:** can you predict the load just from non-brain facts — reaction time, whether they got it right, trial order, timing? **Crucially, this baseline is forbidden from using the number of letters or anything that secretly encodes it** — otherwise it would trivially "win" and tell us nothing. This isolates what the *scalp brain signal* adds beyond ordinary task bookkeeping.
- **Timing-only:** can you win just from the clock/structure of the task? Guards against decoding the task's rhythm instead of the brain.
- **Subject-identity check & artifact check:** make sure the model isn't secretly identifying *who* the person is, or riding on eye-blinks and muscle twitches instead of real brain activity.

**Per-person honesty.** We report results *for each of the nine people separately*, not just one averaged number — because one strong person can hide eight weak ones behind a flattering average. We also require that no single person be propping up the whole result.

**The mechanism half (Half B)** uses the inside-the-brain recordings as a checker (never as something the model gets to use as input). We confirm (1) that the deep theta–alpha coupling really does track memory load in this data, as the literature says, and (2) that the scalp features our model leans on are statistically tied to *that deep coupling channel* — i.e., the surface signal is genuinely an echo of the deep one.

**Our toolkit, smallest-first.** We start with the simplest, most transparent models (plain regularized classifiers) and only climb to fancier ones (compact neural networks) if the simple ones aren't enough. Bigger is not better here; the smallest thing that clears the bar is what we want, both for honesty (simple models are harder to fool yourself with) and for the affordable-hardware mission.

---

## How you'll check it yourself — without trusting us (Slot 8)

This is the part built specifically for you. We commit to building a **verification dashboard**: an openable report (web page + images, plus a script you can run) that for each of the nine held-out people shows, side by side:

1. who the held-out person was (the one the model never saw),
2. their scalp EEG input,
3. the *true* memory load on each trial,
4. the model's scalp-only guess,
5. the baselines' guesses on the same trials,
6. a **deep panel**: the simultaneously-recorded deep memory activity for that person, showing the real activity the scalp readout is tied to,
7. a one-line verdict: does this person **support**, **weaken**, or **contradict** the claim?

Plus a summary view across all nine, so you see the whole picture and not a cherry-picked best case. The test of belief is meant to be plain: *"the model never saw this person, it read their scalp, it called their memory load better than the fair baselines — and the deep recording confirms it was riding the real memory signal."* This dashboard ships **inside** the reproducibility packet, so anyone who downloads our work can check it the exact same way you can. We build it gradually across the project, not in a panic at the end.

---

## What success, failure, and "not yet" each look like — committed before we look (Slots 11, 12, 13)

We write these down *now*, before running anything, so we can't move the goalposts later.

**Success (the concrete bar):** in the held-out (LOSO) high-vs-low memory-load test during maintenance —
- the model's **balanced accuracy** beats the strongest fair baseline by **at least 0.075** (7.5 percentage points) on average, *and*
- it beats that baseline for **at least 7 of the 9 people**, *and*
- no single person, if removed, drags the average improvement below 0.04 (4 points) — i.e. it's not one lucky subject carrying everyone.
- ("Balanced accuracy" just means accuracy fairly adjusted so the model can't win by always guessing the more common answer.)

*One honest escape hatch, fixed in advance:* the very first thing we do in Phase 2 is **count how many memory trials each person actually has.** If that count makes +0.075 unrealistically demanding for legitimate reasons, we propose a replacement bar **before any model is ever run** — never after seeing results. Setting the number is allowed; moving it to fit an outcome is not.

**Mechanism success requires coverage:** the deep-readout half only counts if **at least 5 of the 9 people** have good-enough deep electrode coverage of the memory region (we audit this *before* the mechanism analysis). If fewer than 5 qualify, we are *not allowed* to claim the full deep-readout result, even if the handful we do have looks great.

**Failure (and we report it plainly):**
- *Clean failure:* the model works within a person but **doesn't transfer to held-out strangers**. That's an honest, publishable result — it tells the larger program this first rung needs per-person calibration or more people.
- *Mechanism failure:* the decoding transfers, but the signal turns out **not** to be tied to the deep memory channel (it's riding a generic cortical/task/artifact route). Then we report "transferable load decoding, but not via a validated *deep* signature" — a partial win, not the headline.

**Inconclusive / "not yet":** results swing wildly across the nine people, or the confidence range overlaps the baselines, or too few people have deep coverage. We label it inconclusive — never spun as success. **A clean failure is still a public artifact**; it's a real contribution to knowing where the staircase can and can't go.

---

## Constraints we're working inside (Slot 4)

- **Only 9 people.** This is the biggest limit, and it's why the rigorous held-out testing and per-person reporting matter so much.
- **Consumer hardware** (8 GB GPU) — everything must fit and run here.
- **Licensing:** the dataset is [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) — commercial use is fine with attribution and "share-alike" on adaptations. So: we **never** put the raw data in our code repository (we point readers to the public download); figures carry attribution; any released model weights honor share-alike; our own code ships under a permissive license. Every tool we use must permit commercial use — that's a hard Dandelion rule.
- **Ethics:** de-identified public research data, no human-subject action by us, and **no medical or diagnostic claims** — this is a measurement study, not a clinical tool.
- **No silent exclusions:** if we drop any person, session, channel, or trial, we name it and say why.

---

## What we'll leave behind (Slot 14) and where the money could come from (Slot 15)

**Three deliverables, all required to call the project done:**
1. a rigorous **Technical Report** (for scientists/engineers),
2. an **Accessible Piece** (this document's cousin — the whole story for a general reader),
3. a **Reproducibility Packet** — all the code, pinned dependencies, a plain README, and the verification dashboard, so a stranger can download the public dataset and reproduce every result without contacting us.

**Monetization, honestly:** as a standalone product, this rung is `none identified` — and that's the *right* answer for a first research rung. Its real value is as a **verified stepping stone** that de-risks the larger electrical-fMRI arc and makes the case for the next, better-resourced project. If it succeeds, a near-term path is offering the validated analysis pipeline as a licensed/consulting component to EEG-research groups. The far-horizon path is the north-star device itself: affordable scalp-EEG + AI giving a coarse deep-activity picture — named here only to keep the thread visible, not committed to in this project.

---

## Who's doing what (division of labor)

- **Writing:** Claude drafts the four narrative documents (this sheet, the technical one, the eventual Technical Report and Accessible Piece); Codex reviews and approves each.
- **Building:** Claude owns the data layer (reading the dataset files, aligning events to the brain signals, the held-out testing harness, feature extraction) and the primary decoding pipeline. Codex owns the baselines/statistics and the per-person dashboard rendering. The deep-mechanism analysis is **shared** — Codex leads it, but it rides on Claude's data tooling.
- Any of this can change later through the project's amendment process.

---

## What happens next

The technical Claim Sheet is approved by both agents and Phase 1 is now closed. We've logged a note for you in `director_requests.md` that the Claim Sheet is **ready for your review** whenever you have time — there's nothing blocking us, so we proceed into Phase 2 (building the data reader and counting trials) in the meantime. If you read it and want changes, that just kicks off our normal amendment process; if you approve as-is, we keep going on the current plan.
