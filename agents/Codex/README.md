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
|   `-- Codex Progress Report - Session 8.md
`-- Session Summaries/
    |-- HumanReport1.md
    |-- HumanReport2.md
    |-- HumanReport3.md
    |-- HumanReport4.md
    |-- HumanReport5.md
    |-- HumanReport6.md
    |-- HumanReport7.md
    |-- HumanReport8.md
    |-- HumanReport9.md
    `-- HumanReport10.md
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

- `Progress Reports/`: Periodic director-facing progress reports required by the Dandelion framework. `Codex Progress Report - Session 8.md` summarizes Codex Sessions 1-8.

## Co-owned files outside this workspace

- `Claim Sheet.md`: Agent-approved technical Claim Sheet rev. 2. Phase 1 is closed and Phase 2 is open.
- `Accessible Claim Sheet.md`: Plain-language companion to the technical Claim Sheet, written for Randy and kept in sync through amendments.
- `director_requests.md`: Director-facing request log. Requests 1 and 2 are resolved as of 2026-06-12: Randy approved the Claim Sheet pair and freed disk space for the EEGNet rung.
- `chats/Claude-Codex/Phase 0 Literature Alignment/Phase 0 Literature Alignment - Concluded.md`: Concluded Phase 0 alignment transcript.
- `chats/Claude-Codex/Phase 0 Literature Alignment/Summary.md`: Summary of the concluded Phase 0 alignment.
- `chats/Claude-Codex/Claim Sheet Phase 1/Claim Sheet Phase 1 - Concluded.md`: Concluded Phase 1 review transcript where Codex approved the technical Claim Sheet.
- `chats/Claude-Codex/Claim Sheet Phase 1/Summary.md`: Summary of the concluded Phase 1 review.
- `chats/Claude-Codex/Phase 2 Controls Interface/Phase 2 Controls Interface - Concluded.md`: Concluded interface handoff for Claude's data layer and Codex's controls/statistics/dashboard lane.
- `chats/Claude-Codex/Riemannian Ladder Verdict/Riemannian Ladder Verdict - Active.md`: Active Phase 2 coordination thread for the Riemannian/EEGNet ladder, behavioral-control ablation, mechanism evidence, and the proposed post-EEGNet Claim Sheet amendment.
- `chats/Claude-Codex-Human/Some Updates/Some Updates - Concluded.md`: Concluded thread where Randy approved the Claim Sheet, reported disk space was freed, and clarified the Codex/Claude git protocol.
- `chats/Claude-Codex-Human/Some Updates/Summary.md`: Summary of the concluded Randy/Claude/Codex update thread.
- `scripts/run_control_models.py`: Codex-owned control harness for label-shuffle, behavioral-only, timing-only, and subject-identity diagnostics.
- `scripts/run_behavioral_control_ablation.py`: Codex-owned ablation runner that separates response-time, correctness/match, previous-trial, and trial/session behavioral controls.
- `scripts/run_mtl_bandpower_probe.py`: Codex-owned first mechanism scaffold that summarizes MTL theta/alpha band power and compares it with supplied scalp decoder scores.
- `scripts/run_mtl_residual_coupling_probe.py`: Codex-owned mechanism sensitivity script that tests whether EEGNet score-to-MTL theta-alpha coupling survives load, schedule, and behavioral residualization.
- `scripts/summarize_phase2_amendment_evidence.py`: Codex-owned amendment-support summarizer that compiles completed EEGNet statistics, behavioral-control, bandpower, and residual-coupling outputs into a reproducible evidence packet for the proposed Claim Sheet amendment.
- `scripts/summarize_subject_statistics.py`: Codex-owned subject-level success-criteria summary for signal-vs-control results.
- `scripts/render_verification_dashboard.py`: Codex-owned static dashboard renderer for the director verification path.
- `scripts/audit_mtl_coverage.py`: Co-owned mechanism gate script; now uses the shared MTL anatomy helper.
- `utils/nix_io.py`: Shared NIX reader; Codex added the lazy iEEG epoch loader for mechanism work.
- `utils/mechanism.py`: Shared MTL anatomy helper for hippocampus/amygdala/parahippocampal contact definitions.
- `Project Details/Project Details.md`: Project-wide mission, standards, and EEG-to-LFP idea brief.
- `Project Details/Dataset of human medial temporal lobe neurons, scalp and intracranial EEG during a verbal working memory task.pdf`: Dataset paper provided by the director.

## How to navigate

Start with `Project Details/Project Details.md`, then read `Summary of Only Necessary Context.md`, then check active chats involving Codex. For Codex's Phase 2 controls lane, read `Phase 2 Controls and Statistics Spec.md` before implementing any harness code. For source context, use `Literature Foundation.md` and `references.md`.
