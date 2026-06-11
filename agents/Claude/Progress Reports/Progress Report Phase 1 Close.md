# Progress Report — Phase 1 Close

**Agent:** Claude
**Date/Time:** 2026-06-11 08:43 PDT
**Trigger:** Phase transition — Phase 1 (Sharpening / Claim Sheet) closed; Phase 2 (Execution) begun.
**For:** Randy (the director). Written to be read start to finish without looking anything up.

---

## The one-paragraph version

We finished turning the idea into a signed plan. Both AI agents have now agreed on the **project's contract** — exactly what we're going to test, how we'll know if it worked, and what would count as an honest failure — and I've written a plain-language version of that contract *for you* (`Accessible Claim Sheet.md`). That's the single most important thing to know exists: you can now read one document and understand everything the project has committed to, without wading through the technical sheet. Nothing is blocked on you, and we've already started the actual building. The one thing we'd like from you, whenever it suits you, is a read of that plain-language plan — your review is logged as a formal request and is treated as the project's first chance to amend the plan if you want changes.

## What just happened, in plain terms

A Dandelion project doesn't start building until it has a **Claim Sheet** — a contract that pins down the claim, the method, the success bar, and the failure shapes *before* anyone looks at a single result. That discipline is what keeps a project honest: you can't move the goalposts after the fact if you wrote them down first. Phase 1 was the work of writing and agreeing on that contract.

Here's how it went. I drafted the technical Claim Sheet. Codex reviewed it like a careful second scientist and **didn't rubber-stamp it** — he sent back four specific problems that needed fixing before he'd approve. I agreed with all four, fixed them, and he then gave explicit approval. That back-and-forth is exactly the cross-check the two-agent setup is for, and it genuinely made the plan better. The four fixes are worth knowing because each one closes a way the project could have fooled itself:

1. **We blocked an accidental cheat in one of our comparison tests.** To prove the brain signal is doing real work, we compare our model against a "boring baseline" that's only allowed to use non-brain facts (reaction time, whether they got the answer right, timing). Codex caught that this baseline was at risk of being secretly fed the very thing we're trying to predict — which would make it look artificially strong and muddy the whole comparison. We explicitly forbade that.

2. **We locked *when* in the task we read the brain.** The memory task has three moments: seeing the letters, holding them in mind, and answering. We committed to reading the brain only during the **holding** moment. Why: if we read it during the *seeing* moment, the model could win just by reacting to "more letters appeared on screen" — which is about the eyes, not the memory. Reading during the silent holding period means a signal there is genuinely about the *maintained memory*.

3. **We set the exact passing grade in advance.** Not "better than chance" (which can quietly mean almost nothing), but a concrete bar: the model has to beat the strongest fair baseline by a set margin, do it for at least 7 of the 9 people, and not be secretly propped up by a single lucky person. Writing the number down now means we can't soften it later to manufacture a "win." (There's one honest escape hatch, fixed in advance — see "what's next.")

4. **We set an honesty rule for the 'deep brain' part.** The exciting half of the claim is showing the scalp signal is genuinely tied to the *deep* memory region, not a generic surface shortcut. That check only counts if enough people in the dataset have good-quality deep recordings — Codex pinned the threshold at **at least 5 of the 9 people**. If fewer qualify, we are *not allowed* to claim the full "deep readout" result, even if the handful we have looks great. That rule exists specifically so a partial result never gets reported as the full one.

With those in, Codex approved, and we agreed on who builds what. Then I did the close-out work that's mine by default: wrote your plain-language plan, opened a requests file for you, and updated the contract's status. Phase 1 is closed; the building phase is open.

## The thing built for you

The headline deliverable of this phase, from your point of view, is **`Accessible Claim Sheet.md`** at the project root. It's the entire project — the claim, the method, the success/failure/inconclusive shapes, the way *you* will verify the result yourself, the constraints, and the (honest) monetization picture — written in plain language with links to credible sources for anything you're not expected to already know. The test we held it to: you should be able to read it end to end and come away with an accurate, complete picture, without ever opening the technical sheet. If it fails that test anywhere, tell us — that's a defect we fix.

The most important things in it to sanity-check as the director: the **success bar** (how high we set the passing grade), the **two-halves structure** of the claim (decoding vs. the deep-mechanism proof), and the **verification dashboard** we've committed to building so you can check the result with your own eyes — for each held-out person, side by side: what the model saw, what it guessed, what the fair baselines guessed, and the real deep recording it was supposedly riding on.

## What was surprising / notable

No scientific surprises this phase — it was a planning phase, and the useful signal was *how cleanly the disagreement resolved*. Codex pushed back on four real things, I agreed with all four without a fight because they were correct, and the plan got sharper rather than getting stuck in a loop. That's the collaboration working the way it's supposed to: pushback when warranted, forward motion when the pushback is accepted. The one quietly important realization is that our headline success number (the +0.075 margin) is **provisional until we count the data** — which is the very first thing we do in the building phase. We may discover the dataset is thinner than that bar assumes, in which case we set a fairer bar *before running any model*, never after.

## What's working / what isn't (yet)

- **Working:** the contract is signed by both agents, the plain-language companion exists, the division of labor is settled, and Phase 2 is open with a clear first task.
- **Not yet:** no analysis code exists yet, and the project's Python environment is still empty (no libraries installed). That's the literal next task — installing the tools with exact pinned versions so anyone can reproduce our setup later. Nothing is broken; we're at the start line of the build.
- **One open item on you (non-blocking):** your review of the plan, logged in `director_requests.md`. We are *not* waiting on it — we build in parallel and treat your review, whenever it lands, as the first chance to amend the plan.

## What's next (the building phase begins)

1. **Install the environment** with exact pinned versions (my lane).
2. **Write the data reader** that opens the dataset files and lines up the brain signals with what the person was doing moment to moment — and *validate it against the dataset's own reference loader before trusting it* (a stop-or-go gate; if it doesn't match, we fix it before going further).
3. **Count the trials** — how many memory trials each person actually has, per load level. This is the audit that confirms or replaces the provisional success bar, and it happens *before any model is run*.
4. From there: extract features, run the first held-out-person decoding test, and start building your verification dashboard incrementally.

## Where the files are

- **Your plain-language plan:** `Accessible Claim Sheet.md` (project root) — start here.
- The technical contract: `Claim Sheet.md` (project root).
- Your requests log: `director_requests.md` (project root).
- The full Phase 1 review conversation (now concluded): `chats/Claude-Codex/Claim Sheet Phase 1/` (`...Concluded.md` + `Summary.md`).
