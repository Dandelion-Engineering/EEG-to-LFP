# Summary of Only Necessary Context — Claude

**Last rewritten:** 2026-06-11 (Claude Session 1)
**Current phase:** Phase 0 — Literature Review (NOT yet closed)

> Re-read `/Project Details/Project Details.md` and `AgentPrompt.md` in full at session start — do not duplicate them here. This file only holds what those don't.

## Where the project is right now

Session 1 was the project's **first** working session. Before it, every workspace/chat file was empty. I completed my Phase 0 literature survey. **Phase 0 is not closed yet** — it closes only when *both* agents have written their Literature Foundation and we've reconciled in the alignment chat. Codex has **not** yet done its Phase 0 session (its files were empty as of my session).

## What I produced (Session 1)

- `agents/Claude/Literature Foundation.md` — my 6-section survey. **Read this** to restore the substance.
- `agents/Claude/references.md` — verified bibliography.
- `chats/Claude-Codex/Phase 0 Literature Alignment/...Active.md` — I posted my load-bearing conclusions and proposed first-rung leaning; awaiting Codex.

## The load-bearing conclusions (so the next session doesn't re-derive them)

1. **Frame the project as coupling-signature decoding, NOT direct deep-field recovery.** MTL is ~invisible to scalp EEG as a *field*, but its *coupling to cortex* reaches the scalp. This matches the director's intuition and should anchor the Claim Sheet.
2. **Two same-lab companion papers are gold:** Boran 2019 (Science Advances, DOI 10.1126/sciadv.aav3687 — load-dependent hippocampal firing + hippocampus-cortex theta-alpha coupling) and Fedele 2020 (bioRxiv 2020.06.05.136515 — hippocampal-sEEG↔**scalp-EEG** theta phase-locking, peaks at **left parietal P3**). They prove a scalp-detectable deep trace exists *in our exact data* and point at channel/band (P3, theta).
3. **Closest prior art = NeuroFlowNet (arXiv:2603.03354, 2026)**, conditional normalizing flow reconstructing deep-temporal-lobe iEEG from scalp EEG. Differentiate from it: foreground deep-state validation + LOSO generalization, don't just redo waveform mimicry. **TODO: extract its numeric metrics + which dataset from full PDF.**
4. **Central bet supported:** ML decodes deep-origin info from "surface-negative" scalp EEG that human readers miss (Constantino 2021, Roehri Epilepsia 10.1002/epi.70061). But detectable ≠ fully reconstructable — claim honestly.
5. **Top methodological risk = leakage with only 9 subjects.** Bake **leave-one-subject-out (LOSO)** into success/non-transfer shapes from the start. Most likely false-success mode.

## My proposed first rung (to settle with Codex in Phase 1)

Candidate directions, easy→hard: **A** = scalp-only single-trial decoding of a deep-validated WM state (load / coupling magnitude, checked vs. iEEG+units); **B** = scalp→MTL theta band-power time-course reconstruction (correlation vs. true iEEG, held-out subjects); **C** = full scalp→iEEG waveform reconstruction (overlaps NeuroFlowNet); **D** = reach toward MTL population firing (hardest, uses the unit data, likely later rung). **My lean: A as the first rung, B as fast-follow.** Both fit 8 GB VRAM and build reusable infra (loader, alignment, LOSO harness, metrics).

## Key facts about the substrate

- Dataset: `D:\Simultaneous EEG_LFP`. 9 subjects, modified Sternberg verbal WM task (encoding/maintenance/recall separated). Simultaneous scalp EEG (10-20) + iEEG depth + 1526 MTL single units + MNI coords/labels + trial metadata. Format **NIX/HDF5** (`.h5`), MATLAB loader provided (`code_MATLAB/Load_Data_Example_Script.m`). **License CC BY-SA 4.0** — commercial use OK.
- Compute: RTX 4070 Laptop, **8 GB VRAM**, 16 GB RAM, ~850 GB free on D:. Favors compact models, per-band/region targets, fine-tuning not from-scratch foundation models.
- Python: ALWAYS use `.\venv\Scripts\python.exe` and `.\venv\Scripts\pip.exe`. Never bare `python`/`pip`. venv exists at project root.

## Open items to carry into Phase 1

- Resolve CC BY-SA **ShareAlike** interaction with derived model weights / released report (flagged to Codex; I read it as probably-fine but worth confirming).
- Decide hand-crafted features vs. pretrained EEG encoder (LaBraM arXiv:2405.18765 etc.) for the first rung — verify license + 8 GB VRAM fit before adopting any. My lean: hand-crafted first.
- Extract NeuroFlowNet metrics/dataset from full PDF.

## Process reminders specific to me

- I'm the **default writer** for Claim Sheet, Accessible Claim Sheet, Technical Report, Accessible Piece (Codex reviews/approves).
- My **next progress report** is due at my **Session 8**, or sooner if my session closes a phase transition or an approved amendment.
- `director_requests.md` doesn't exist yet — create it at project root when the first director-only need arises (the Phase-1-close Claim Sheet review will be the first entry).
- Cross-review: each session, read the most recent unreviewed human report from the other agent + the work it points to + relevant active chats. (Session 1 had nothing to review — Codex hadn't worked yet.)
