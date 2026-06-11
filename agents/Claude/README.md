# Claude — Workspace

This is Claude's personal workspace for the Dandelion "EEG → deep/MTL activity" project (the first standalone rung toward the long-term "electrical fMRI" goal: reconstructing deep-brain activity from cheap scalp EEG + AI, validated against the simultaneous scalp/iEEG/MTL-unit dataset on `D:\Simultaneous EEG_LFP`).

## Folder tree

```
agents/Claude/
├── README.md                          ← this file: how to navigate my workspace
├── Summary of Only Necessary Context.md  ← AUTHORITATIVE continuity handoff; rewritten every session
├── Literature Foundation.md           ← Phase 0 deliverable: my survey of the field (6 sections)
├── references.md                      ← AUTHORITATIVE running bibliography; verified links/DOIs
├── Session Summaries/                 ← human-readable per-session reports
│   └── HumanReport1.md
└── Progress Reports/                  ← director-facing reports every 8th session + at phase/amendment events
    (empty until session 8 or a phase transition)
```

## What each file is for

- **Summary of Only Necessary Context.md** — The single file I re-read first each session to restore where the work stands. Authoritative for "current state." Completely rewritten at the end of every session.
- **Literature Foundation.md** — My independent Phase 0 literature survey. Stable once Phase 0 closes; informs the Claim Sheet. Not overwritten — it's a recorded turn.
- **references.md** — Every source that informed my work, with a verified link/DOI and a note on how it shaped the project. Authoritative; appended to as the project grows. Reconciled with Codex's references into the Technical Report bibliography at Phase 2.
- **Session Summaries/** — One human-readable report per session (`HumanReport<N>.md`), written for the director. Authoritative record of session history.
- **Progress Reports/** — Separate from session summaries. Director-facing deep-dives written every 8th of my sessions and at phase transitions / approved amendments. Empty until the first such trigger.

## Authoritative vs. scratch

All current files are authoritative. There is no scratch/temp content yet. If I add scratch work later, it will live in a clearly labeled `scratch/` subfolder.

## Files I own or co-own outside this folder

- `chats/Claude-Codex/...` — I co-own chat threads with Codex (currently: *Phase 0 Literature Alignment*).
- Per the framework's default writer convention, I am the **default writer** for the project's four narrative deliverables — the Claim Sheet, the Accessible Claim Sheet, the Technical Report, and the Accessible Piece (Codex reviews and approves each). These don't exist yet; they'll be created in Phase 1 (Claim Sheets) and Phase 3 (reports), at the project root or a deliverables folder TBD with Codex.

## How to navigate without prior context

Start with **Summary of Only Necessary Context.md** for the current state, then **Literature Foundation.md** for the grounding, then the latest file in **Session Summaries/** for the most recent narrative. The shared project framework lives in `/Project Details/` and `AgentPrompt.md` at the project root.
