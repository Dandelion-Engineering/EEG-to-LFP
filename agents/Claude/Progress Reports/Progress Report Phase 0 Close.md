# Progress Report — Phase 0 Close

**Agent:** Claude
**Date/Time:** 2026-06-11 07:02 PDT
**Trigger:** Phase transition — Phase 0 (Literature Review) closed; Phase 1 (Claim Sheet) begun.
**For:** Randy (the director). Written to be read start to finish without looking anything up.

---

## The one-paragraph version

We finished the "read the field before committing" phase. Both AI agents independently surveyed the science, then compared notes — and we landed in the same place without having coordinated, which is a good sign the reading is solid. We've agreed on what the **first real project** should be: not the whole "electrical fMRI" dream at once, but the smallest honest first step toward it. I've now written that step up as a formal plan (the Claim Sheet) and handed it to Codex to review. Nothing is blocked on you yet. The first thing we'll need from you is a look at that plan once Codex and I finish agreeing on it.

## What this project is, in plain terms

When your neurons fire, they make tiny electrical signals. **EEG** is a cheap, painless way to measure some of those signals using sensors on the scalp — no surgery, no big machine. The catch: by the time a signal from *deep* inside the brain reaches the scalp, it's faint and smeared, because the skull is a poor conductor of electricity (about 80 times worse than brain tissue). So the conventional wisdom is that deep structures — like the **medial temporal lobe (MTL)**, the brain's memory hub — are basically invisible to scalp EEG.

Your idea pushes back on that. Deep structures don't sit in isolation; they're wired to the outer brain (the cortex), and they "talk" to it in rhythmic patterns during memory tasks. Even if we can't see the deep signal *directly* at the scalp, that *conversation* between deep and surface might leave a detectable fingerprint up top. The bet of the project: **AI can learn to read that fingerprint** and tell us something real about deep brain activity from cheap scalp recordings alone.

The reason this is testable rather than just a nice story is the dataset you found. It contains, from the same people at the same moments: scalp EEG (the cheap signal), *and* recordings taken from electrodes placed deep inside the brain during epilepsy surgery (the expensive "ground truth" we normally never get). So we can take the scalp signal, make a guess about what's happening deep down, and **check our guess against the real deep recording.** That's what turns this from speculation into measurement.

> Background, if you want to go deeper: the dataset and task are described in [Boran et al., *Scientific Data* 2020](https://www.nature.com/articles/s41597-020-0364-3). The deep-to-surface "conversation" during memory was shown in [Boran et al., *Science Advances* 2019](https://www.science.org/doi/full/10.1126/sciadv.aav3687).

## What we decided in this phase

Phase 0's whole job was to read the existing science so our plan is grounded in what's already known, not invented on the spot. Codex and I each did our own survey, then compared. Four decisions came out of it:

1. **We're not claiming we can directly "see" deep brain activity from the scalp.** The honest, achievable first claim is that the scalp carries a *signature* of deep activity, by way of that deep-to-surface conversation. This matches your original intuition exactly.

2. **The first step is a memory-state read-out, not a full reconstruction.** The people in the dataset were doing a memory task (hold a few letters in mind, then answer). The deep brain's behavior changes with how *much* they're holding in mind ("memory load"). Our first claim: **from scalp EEG alone, predict a person's memory load — on a person the AI has never seen before — better than honest baseline guesses, and show that the scalp signal it's using is genuinely tied to the deep-brain conversation** (confirmed by the deep recordings). It's a small, checkable claim that's still a real first rung on the ladder toward the bigger goal.

3. **The single biggest trap, and how we're avoiding it.** With only **9 people** in the dataset, it's dangerously easy to get a result that looks great but is fake — the AI can secretly memorize quirks of specific individuals instead of learning something general. Our guard against this is the strictest honest test there is: **train the AI on some people, then test it on a completely held-out person it never saw.** ("Leave-one-subject-out.") Anything less can flatter us with fake success. We've built this into the plan as the *headline* test, not an afterthought.

4. **There's recent related work — we differentiate from it.** A 2026 method called NeuroFlowNet reconstructs deep brain signals from scalp EEG on a related dataset. But it trains a separate model per person, needs a bigger graphics card than your laptop has, and doesn't test the "never-seen-before person" generalization. So we have three clean ways to do something genuinely new: **(a)** test on unseen people, **(b)** run on affordable consumer hardware (your 8 GB laptop GPU), and **(c)** verify the read-out is tied to the *real deep signal*, not just a plausible-looking trace.

## What was surprising

The most useful surprise was how *specific* the existing science already is about where to look. A companion study to our dataset ([Fedele et al. 2020](https://www.biorxiv.org/content/10.1101/2020.06.05.136515v1.full)) found that the deep-memory-hub signal shows up most strongly at one particular scalp location (left-parietal, near a sensor called "P3") in one particular rhythm band ("theta," a slow ~6–7 Hz brain rhythm). That's a concrete head-start: we're not searching blind. The other quiet surprise was the strength of the agreement between the two agents — when two independent surveys converge this cleanly, it raises confidence that the plan is built on the field's real consensus rather than one agent's idiosyncratic read.

## What's working / what isn't (yet)

- **Working:** the literature foundation is solid, the agents agree, the dataset is confirmed present and readable in principle, and the plan is now written down as a contract.
- **Not yet done (normal for this stage):** no analysis code exists yet, and the project's Python environment is currently empty (no analysis libraries installed) — setting that up cleanly, with exact pinned versions so anyone can reproduce it, is the first task of the next phase. Nothing is broken; we're simply at the start of the build.

## What's next

1. Codex reviews the Claim Sheet; he and I settle a few specifics (exactly how we measure "load," the statistical bar for success at n=9, who builds what).
2. Once we agree, I write the **Accessible Claim Sheet** — a plain-language companion to the technical plan, written for you — and log a request for you to review the plan whenever it suits you. **That review will be the first thing we ask of you.**
3. Then Phase 2 (the actual building) begins: install the environment, write the data reader, extract features, run the first held-out-person decoding test, and start the per-person **verification dashboard** — the thing you'll eventually open to check the result yourself, without taking our word for it.

## Where the files are

- The plan: `Claim Sheet.md` (project root).
- The Phase 0 surveys: `agents/Claude/Literature Foundation.md` and `agents/Codex/Literature Foundation.md`.
- The agents' agreement record: `chats/Claude-Codex/Phase 0 Literature Alignment/Summary.md`.
- The live review conversation: `chats/Claude-Codex/Claim Sheet Phase 1/`.
