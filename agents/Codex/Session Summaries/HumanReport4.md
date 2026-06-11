# Human Report 4 - Codex

**Date/Time:** 2026-06-11 09:05 PDT
**Agent:** Codex
**Session:** 4
**Phase:** Phase 2 - Execution open; controls/statistics interface prepared

## Summary

This session began by checking for `.codex-session.lock` in the project root. No lock existed, so I created it before doing project work. I then read the automation memory, `AgentPrompt.md`, `Project Details/Project Details.md`, the dataset paper in `Project Details/`, Codex continuity files, Claude's current continuity file, the concluded Phase 0 and Phase 1 chat summaries, the Claim Sheet, the Accessible Claim Sheet, and `director_requests.md`.

The main finding was that Codex's own continuity file was stale relative to the repository. It still said Phase 1 was open and the Accessible Claim Sheet/director request were pending, but the current repository shows that Claude Session 3 completed those closeout tasks, concluded the Phase 1 chat, committed the work, and opened Phase 2. I treated the current repository as authoritative and rewrote Codex continuity at the end of this session.

Because no Phase 2 data-layer code exists yet, I did not implement or run the controls harness. Claude's own continuity file says Codex's executable lanes unblock after the pinned dependency install, NIX reader, aligned epoch output, and pre-model trial-count audit. Instead, I made a scoped Phase 2 contribution that should help that work land cleanly: a Codex-owned controls/statistics interface specification and a new Claude-Codex handoff chat.

## What was accomplished

1. **Verified Phase 2 is open.**

   I confirmed the technical Claim Sheet now says Phase 1 is closed and Phase 2 is open. I also confirmed `Accessible Claim Sheet.md` exists and matches the same high-level commitments, and that `director_requests.md` contains the non-blocking director review request.

2. **Confirmed there were no active Codex chats needing a reply.**

   The Phase 0 Literature Alignment chat and Phase 1 Claim Sheet Review chat are both concluded and have summaries. No active chat existed at the start of this session.

3. **Created the Phase 2 controls/statistics specification.**

   New file:

   - `agents/Codex/Phase 2 Controls and Statistics Spec.md`

   The spec defines the data-layer output contract Codex will need for the controls harness and dashboard: trial metadata, epoch/window metadata, feature bundle shape, explicit forbidden inputs for behavioral/timing controls, label-shuffle rules, subject-level evidence, trial-count audit outputs, and the verification-dashboard prediction table. It also restates the hard guards from the Claim Sheet: trial-count audit before modeling, held-out subject touched once, no window leakage, behavioral controls excluding the target, and no silent exclusions.

4. **Opened a new Claude-Codex coordination chat.**

   New active chat:

   - `chats/Claude-Codex/Phase 2 Controls Interface/Phase 2 Controls Interface - Active.md`

   I used it to notify Claude of the spec and to request that the NIX reader/aligned-epoch layer preserve the fields needed for controls and leakage checks. I specifically flagged `previous_trial_correct` as useful because the dataset paper states incorrect trials are always followed by set-size-4 trials, which could create a trial-order confound.

5. **Kept modeling blocked until the required audit.**

   No dependency install, feature extraction, decoding, or model evaluation was run. This was intentional: the Claim Sheet requires maintenance-period trial counts before any decoder result is observed, and the data reader does not exist yet.

## Important decisions

- Codex's Phase 2 implementation should wait for Claude's aligned trial/epoch output, but Codex can still specify the interface now so the reader does not omit key control metadata.
- The controls harness should treat forbidden control inputs as explicit validation failures, not as a documentation note.
- The trial-count audit should surface discussion triggers before modeling: zero or very thin class counts, severe class imbalance, large exclusions, or counts that disagree with reference metadata.
- The verification dashboard should consume a fold-level predictions table with both signal and control predictions so the director can inspect each held-out subject without reconstructing pipeline internals.

## Challenges

- The automation memory and Codex restart summary were stale relative to the repository. The current `git log` and project files show Claude Session 3 is already committed at `94312f5`, while Codex's local summary still described Phase 1 as open. I corrected this in the rewritten summary.
- `pdftotext` extracted the dataset paper text but emitted MiKTeX configuration warnings about an empty font-map configuration. The warning did not block reading the paper.
- There is no Phase 2 analysis code yet, so an executable controls harness would have been premature.

## Files created or updated

- `agents/Codex/Phase 2 Controls and Statistics Spec.md`
- `chats/Claude-Codex/Phase 2 Controls Interface/Phase 2 Controls Interface - Active.md`
- `agents/Codex/Session Summaries/HumanReport4.md`
- `agents/Codex/README.md`
- `agents/Codex/Summary of Only Necessary Context.md`

## Next steps

1. Claude should install pinned dependencies, create the NIX reader, validate it against the dataset reference structure, and produce the pre-model trial-count audit.
2. Claude should respond in the new Phase 2 Controls Interface chat if any requested field or output shape conflicts with the NIX structure.
3. Codex should implement the controls/statistics harness only after the aligned epoch output and trial-count audit exist.
4. If the trial-count audit suggests the +0.075 success bar is unfair, Claude and Codex should agree a replacement in chat before any model run.
5. Randy's Claim Sheet review remains open in `director_requests.md`, but it is non-blocking.
