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
│   ├── HumanReport1.md
│   ├── HumanReport2.md
│   └── HumanReport3.md
└── Progress Reports/                  ← director-facing reports every 8th session + at phase/amendment events
    ├── Progress Report Phase 0 Close.md
    └── Progress Report Phase 1 Close.md
```

## What each file is for

- **Summary of Only Necessary Context.md** — The single file I re-read first each session to restore where the work stands. Authoritative for "current state." Completely rewritten at the end of every session.
- **Literature Foundation.md** — My independent Phase 0 literature survey. Stable once Phase 0 closes; informs the Claim Sheet. Not overwritten — it's a recorded turn.
- **references.md** — Every source that informed my work, with a verified link/DOI and a note on how it shaped the project. Authoritative; appended to as the project grows. Reconciled with Codex's references into the Technical Report bibliography at Phase 2.
- **Session Summaries/** — One human-readable report per session (`HumanReport<N>.md`), written for the director. Authoritative record of session history.
- **Progress Reports/** — Separate from session summaries. Director-facing deep-dives written every 8th of my sessions and at phase transitions / approved amendments. Contains `Progress Report Phase 0 Close.md` (Phase 0 → Phase 1, Session 2) and `Progress Report Phase 1 Close.md` (Phase 1 → Phase 2, Session 3). Neither is a cadence report, so my first cadence report is still due at my Session 8.

## Authoritative vs. scratch

All current files are authoritative. There is no scratch/temp content yet. If I add scratch work later, it will live in a clearly labeled `scratch/` subfolder.

## Files I own or co-own outside this folder

- `utils/` (project root) — **data layer (Session 4).** `nix_io.py` (NIX session reader: aligned scalp epochs, trial metadata, lazy iEEG/electrode access), `epoching.py` (maintenance-window extraction). Shared module imported by all scripts per Standards.
- `scripts/` (project root) — **Phase 2 data-layer scripts (Session 4).** `validate_nix_reader.py` (stop-or-go reader gate, 20/20 pass), `build_trial_metadata.py` (project-wide trial table — the contract Codex's controls harness consumes), `audit_trial_counts.py` (pre-model trial-count + montage audit).
- `requirements.txt` (project root) — pinned, commercial-OK dependencies (Session 4).
- `outputs/` (project root, **gitignored / local-only**, rebuildable) — `trial_metadata.{csv,parquet}`, `session_summary.csv`, `scalp_montage.json`, `trial_count_audit.{md,csv}`, `trial_count_by_setsize.csv`, `montage_intersection.json`.
- `chats/Claude-Codex/...` — I co-own chat threads with Codex (*Phase 0 Literature Alignment* — concluded; *Claim Sheet Phase 1* — concluded; *Phase 2 Controls Interface* — **active**, I replied Session 4 with the data-layer field mapping + audit results + the open montage question).
- `Claim Sheet.md` (project root) — I am the default writer; **agent-approved rev. 2; Phase 1 closed Session 3**.
- `Accessible Claim Sheet.md` (project root) — my default-writer companion to the Claim Sheet; **written Session 3**. Kept in sync with the technical sheet via the amendment protocol.
- `director_requests.md` (project root) — co-owned operational log; I opened it Session 3 with the *Claim Sheet ready for director review* entry.
- Per the framework's default writer convention, I am the **default writer** for the project's four narrative deliverables — the Claim Sheet, the Accessible Claim Sheet, the Technical Report, and the Accessible Piece (Codex reviews and approves each). The Technical Report and Accessible Piece are Phase 3 and don't exist yet.

## How to navigate without prior context

Start with **Summary of Only Necessary Context.md** for the current state, then **Literature Foundation.md** for the grounding, then the latest file in **Session Summaries/** for the most recent narrative. The shared project framework lives in `/Project Details/` and `AgentPrompt.md` at the project root.
