# Codex Workspace README

## Folder tree

```text
agents/Codex/
|-- Literature Foundation.md
|-- Phase 1 Claim Sheet Review Scaffold.md
|-- Phase 2 Controls and Statistics Spec.md
|-- README.md
|-- references.md
|-- Summary of Only Necessary Context.md
|-- Progress Reports/
`-- Session Summaries/
    |-- HumanReport1.md
    |-- HumanReport2.md
    |-- HumanReport3.md
    |-- HumanReport4.md
    |-- HumanReport5.md
    `-- HumanReport6.md
```

## Authoritative files

- `Literature Foundation.md`: Codex's Phase 0 scientific and technical foundation for the EEG-to-LFP project.
- `Phase 1 Claim Sheet Review Scaffold.md`: Codex's technical review checklist for the Phase 1 Claim Sheet, focused on targets, subject-held-out splits, leakage controls, metrics, licensing, and reproducibility.
- `Phase 2 Controls and Statistics Spec.md`: Codex's Phase 2 interface specification for controls, statistics, trial-count audit expectations, leakage guards, and verification-dashboard inputs.
- `references.md`: Codex's running bibliography with notes on how each source shaped the project.
- `Summary of Only Necessary Context.md`: The restart document. It is rewritten at the end of each Codex session and should be read after `Project Details/` at the start of the next session.
- `Session Summaries/`: Human-readable reports for each Codex session.
- `README.md`: This navigation file.

## Temporary or periodic files

- `Progress Reports/`: Reserved for every-eighth-session reports or phase/amendment progress reports required by the Dandelion framework. Codex has not yet needed one.

## Co-owned files outside this workspace

- `Claim Sheet.md`: Agent-approved technical Claim Sheet rev. 2. Phase 1 is closed and Phase 2 is open.
- `Accessible Claim Sheet.md`: Plain-language companion to the technical Claim Sheet, written for Randy and kept in sync through amendments.
- `director_requests.md`: Director-facing request log. Request 1 asks Randy to review the Claim Sheet and Accessible Claim Sheet; it is non-blocking.
- `chats/Claude-Codex/Phase 0 Literature Alignment/Phase 0 Literature Alignment - Concluded.md`: Concluded Phase 0 alignment transcript.
- `chats/Claude-Codex/Phase 0 Literature Alignment/Summary.md`: Summary of the concluded Phase 0 alignment.
- `chats/Claude-Codex/Claim Sheet Phase 1/Claim Sheet Phase 1 - Concluded.md`: Concluded Phase 1 review transcript where Codex approved the technical Claim Sheet.
- `chats/Claude-Codex/Claim Sheet Phase 1/Summary.md`: Summary of the concluded Phase 1 review.
- `chats/Claude-Codex/Phase 2 Controls Interface/Phase 2 Controls Interface - Concluded.md`: Concluded interface handoff for Claude's data layer and Codex's controls/statistics/dashboard lane.
- `scripts/run_control_models.py`: Codex-owned control harness for label-shuffle, behavioral-only, timing-only, and subject-identity diagnostics.
- `scripts/summarize_subject_statistics.py`: Codex-owned subject-level success-criteria summary for signal-vs-control results.
- `scripts/render_verification_dashboard.py`: Codex-owned static dashboard renderer for the director verification path.
- `Project Details/Project Details.md`: Project-wide mission, standards, and EEG-to-LFP idea brief.
- `Project Details/Dataset of human medial temporal lobe neurons, scalp and intracranial EEG during a verbal working memory task.pdf`: Dataset paper provided by the director.

## How to navigate

Start with `Project Details/Project Details.md`, then read `Summary of Only Necessary Context.md`, then check active chats involving Codex. For Codex's Phase 2 controls lane, read `Phase 2 Controls and Statistics Spec.md` before implementing any harness code. For source context, use `Literature Foundation.md` and `references.md`.
