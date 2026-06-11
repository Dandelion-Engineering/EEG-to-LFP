# Human Report 1 — Claude

**Date/Time:** 2026-06-11 05:46 PDT
**Agent:** Claude
**Session:** 1
**Phase:** 0 — Literature Review

---

## Summary

This was the project's first real working session. Every workspace and chat file was empty when I started, so the session's job was to lay Phase 0's foundation: survey the field the idea sits in, well enough that when we write the Claim Sheet in Phase 1, its method choices, baselines, metrics, and success/failure definitions are grounded in what researchers have already established rather than guessed.

### What was accomplished

1. **Read the full project framework and the dataset.** Confirmed the substrate on disk (`D:\Simultaneous EEG_LFP`): 9 epilepsy patients performing a verbal working-memory task (a "modified Sternberg" task — letters are shown, held in mind, then tested), recorded *simultaneously* at three depths — scalp EEG, intracranial EEG from depth electrodes, and 1,526 individual neurons in the medial temporal lobe (the memory-central deep brain region). Confirmed the dataset's license is **CC BY-SA 4.0**, which permits commercial use — important because Dandelion only uses commercially-usable resources.

2. **Conducted the literature survey and wrote the Literature Foundation** (`agents/Claude/Literature Foundation.md`) — a six-section document covering the methods landscape, typical performance ranges, available datasets/tools, known failure modes, open questions, and references. Every source carries a verified working link or DOI (no citing from memory — a framework rule for Phase 0).

3. **Built the references file** (`agents/Claude/references.md`) with citation-ready entries.

4. **Opened the Phase 0 alignment chat with Codex** (`chats/Claude-Codex/Phase 0 Literature Alignment/`) summarizing my load-bearing conclusions so we can reconcile our two independent readings of the field before Phase 1 starts.

### The core findings (in plain terms)

- **Why this project is even possible.** The hard part of "reading deep brain activity from a cheap scalp cap" has always been the lack of ground truth to check against. This dataset is special because it records the scalp *and* the deep brain at the same moment in the same person — so any guess we make from the scalp can be checked against what was really happening deep inside. That is what turns the idea from speculation into something measurable.

- **The right way to frame the problem.** Classical brain-imaging theory says deep structures like the hippocampus are essentially *invisible* to a scalp cap — the skull blurs and weakens their signal too much (the skull conducts electricity ~80× worse than brain tissue). But deep structures constantly "talk to" the outer brain (the cortex), and *that* conversation does reach the scalp. So the realistic path isn't to photograph the deep field directly; it's to learn the deep region's **fingerprint in how it drives the cortex** — which is exactly the intuition in the original Faraday idea. I think this reframing should anchor the whole Claim Sheet.

- **Two companion papers from the same lab are unusually useful.** The group that recorded our dataset already published analyses showing that during this exact memory task, the hippocampus's activity rises with memory load and synchronizes with the cortex in the "theta–alpha" rhythm range — and crucially, that this synchronization is *measurable on the scalp EEG itself*, peaking at one specific electrode over the left parietal area. In other words, prior work using this very data already found a deep-brain trace at the scalp and even told us where to look.

- **The central bet is supported by other fields.** In epilepsy research, machine learning routinely picks deep-brain events out of scalp EEG that trained human readers score as "nothing there." That is strong evidence that scalp EEG carries far more deep-origin information than the eye can see — the bet this whole project rests on. (Honesty caveat: "detectable" is not the same as "fully reconstructable," and I've been careful not to overstate it.)

- **The closest existing work is very recent (2026).** A method called NeuroFlowNet already reconstructs intracranial signals across the deep temporal lobe from scalp EEG. This is good news (it proves the approach is tractable and worth publishing) and a challenge (we shouldn't just repeat it). My recommendation is to differentiate by foregrounding *validation against the deep ground truth* and by proving the result *generalizes to people the model has never seen* — see the risk below.

### Important decisions I made

- **Recommended framing the project around coupling-signature decoding, not direct deep-field recovery** — the evidence points strongly this way and it matches the director's own instinct.
- **Flagged leave-one-subject-out testing as non-negotiable from the start.** With only 9 people in the dataset, the single most likely way to produce a result that *looks* like a success but isn't is to accidentally let the model memorize individuals. Testing on people it never trained on is the guard, and I want it written into the success/failure definitions in the Claim Sheet rather than bolted on later.
- **Proposed candidate "first rungs"** for the project (ordered easy→hard) and recommended starting with either decoding a deep-validated memory state from the scalp, or reconstructing the deep theta-rhythm time-course — both give a sharp, checkable claim, both fit our modest laptop GPU, and both build infrastructure the harder versions will reuse.

### Reasoning paths explored

I considered whether to push straight for the most ambitious "reconstruct the deep waveform" target (direction C) but concluded that (a) the 2026 NeuroFlowNet work already partly occupies it, and (b) it's a poor *first* rung — higher risk, harder to verify cleanly, and it skips the infrastructure the smaller claims would build. I also weighed whether to lean on large pretrained "EEG foundation models" given our small dataset; my lean is to stay lean and hand-craft features grounded in the coupling literature for the first rung, treating pretrained models as a later upgrade if needed.

### Challenges

No real obstacles this session — the dataset and framework were clear, and the literature was rich and accessible. The main *open* challenge I'm carrying forward is a licensing nuance: the dataset's "ShareAlike" clause is fine for commercial use, but I want to confirm in Phase 1 how it interacts with model weights and our released report. I've flagged it for Codex.

### Files created/updated this session

- `agents/Claude/Literature Foundation.md` (new) — the Phase 0 deliverable
- `agents/Claude/references.md` (new) — running bibliography, verified links/DOIs
- `agents/Claude/README.md` (new) — workspace guide
- `agents/Claude/Summary of Only Necessary Context.md` (rewritten) — continuity handoff
- `chats/Claude-Codex/Phase 0 Literature Alignment/Phase 0 Literature Alignment - Active.md` (new) — alignment chat opened
- `agents/Claude/Session Summaries/HumanReport1.md` (this file)
- Created empty `Session Summaries/` and `Progress Reports/` folders

### Next steps / pending actions

1. **Codex runs its own Phase 0 session** — writes an independent Literature Foundation, then replies in the alignment chat. Phase 0 does **not** close until both Foundations exist and we've reconciled.
2. **Reconcile in chat**, agree on load-bearing sources and the candidate first-rung direction.
3. **Begin Phase 1** — draft the Claim Sheet, then the Accessible Claim Sheet, decide the division of labor, and log a "Claim Sheet ready for director review" entry in `director_requests.md` (that file doesn't exist yet; it will be created when the first director-only need arises, which is the Phase-1-close review).
4. **Carry-forward action items:** extract NeuroFlowNet's numeric metrics + dataset from its full PDF; resolve the CC BY-SA ShareAlike question; decide hand-crafted-features vs. pretrained-encoder for the first rung.

**Randy — nothing is blocked on you yet.** The first thing that will need you is reviewing the Claim Sheet once Codex and I finish Phase 1; I'll log that request in `director_requests.md` when we get there.
