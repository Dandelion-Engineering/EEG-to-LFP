# Summary — Phase 0 Literature Alignment

**Date Range:** 2026-06-11 (Claude Session 1) → 2026-06-11 (Claude Session 2)
**Participants:** Claude, Codex
**Status:** Concluded. This chat closed Phase 0 (Literature Review).

## Purpose

Compare the two agents' independent Literature Foundation documents, surface discrepancies, and align on which sources are load-bearing before Phase 1 (Claim Sheet) begins.

## Outcome

The two independent readings of the field **converged strongly**. No substantive discrepancies. Phase 0 is closed; Phase 1 begins with Claude drafting the Claim Sheet and Codex reviewing.

## Aligned conclusions (load-bearing into Phase 1)

1. **Frame as coupling-signature / deep-state decoding, NOT direct MTL field recovery.** MTL is ~invisible to scalp EEG as a *field*; its *coupling to cortex* leaves a scalp-detectable signature. Matches the director's intuition.
2. **First rung = Candidate A:** scalp-only, single-trial prediction of an intracranially-validated MTL working-memory state, evaluated **leave-one-subject-out (LOSO)**. Candidate B (scalp→MTL theta/alpha band-power time-course reconstruction) is the pre-declared fast-follow.
3. **Target hygiene (Codex's key refinement, adopted):** primary target = **working-memory load (set size)** — a task variable independent of any neural channel; iEEG theta–alpha coupling + MTL unit firing serve as the **mechanistic validation layer**, not the predicted target. This avoids circularity. A "mechanism-direct" variant (predict an intracranially-defined coupling state from scalp-only features) is a pre-declared extension.
4. **LOSO is the headline; within-subject is diagnostic only.** Leakage with 9 subjects is the single most likely false-success mode. Controls baked in from the start: label-shuffle, behavioral-only, timing-only, autocorrelation/window-leakage guard, subject-identity check, artifact sanity.
5. **Model ladder:** hand-crafted band/covariance/coupling features + regularized linear/LDA first; Riemannian as small-data diagnostic; EEGNet/foundation models only as later optional comparisons. No foundation models in the first rung.
6. **NeuroFlowNet (arXiv:2603.03354) is the closest prior art** — differentiate, don't reproduce. It is subject-specific (S1/S6/S9, 90/10 trial split), trained on RTX 4080/16 GB, reports alpha-FC relative error (full model mean 0.157 vs linear-regression 1.000). Our three differentiators: subject-held-out generalization, 8 GB consumer-hardware efficiency, deep-state validation over waveform mimicry.

## Resolved open items

- **Fedele 2020** scalp-hippocampal coupling preprint verified stable at bioRxiv [10.1101/2020.06.05.136515](https://www.biorxiv.org/content/10.1101/2020.06.05.136515v1.full); group has a 2022 published follow-on (PMC9374435). P3/theta evidence is solid.
- **CC BY-SA 4.0:** manageable, not a blocker. Raw data stays out of the repo; derived figures/reports carry attribution; trained weights / released derived datasets treated as ShareAlike-sensitive until the Claim Sheet records a precise policy; Dandelion code stays permissive. To be written as explicit Claim Sheet policy.
- **Foundation-model transfer:** deferred. Not the first move.

## Environment facts confirmed this session

- Dataset at `D:\Simultaneous EEG_LFP`: 37 NIX `.h5` files in `data_nix/`, `code_MATLAB/` loader, `NIX_File_Structure.pdf`, `Subject_Characteristics.pdf`, `README.md`, `LICENSE` (CC BY-SA 4.0). 9 subjects, modified Sternberg verbal WM task.
- `venv` exists (Python 3.11.9) but is **bare** — no numpy/scipy/h5py/mne/scikit-learn/nixio/torch. Phase 2 needs a pinned dependency stack; data is NIX-format HDF5 (`nixio` reads natively, license check pending).

## Where it goes next

New chat `chats/Claude-Codex/Claim Sheet Phase 1/` for the Claim Sheet draft + Codex review. Division-of-labor proposal to be ratified there. The Phase-1-close *Claim Sheet ready for director review* entry will be the project's first `director_requests.md` entry.
