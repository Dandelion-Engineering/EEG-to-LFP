# Summary of Only Necessary Context — Claude

**Last rewritten:** 2026-06-11 (Claude Session 3)
**Current phase:** **Phase 2 — Execution (OPEN).** Phase 1 closed this session. No analysis code exists yet.

> Re-read `/Project Details/Project Details.md` and `AgentPrompt.md` in full at session start — do not duplicate them here. This file only holds what those don't.

## Where the project is right now

- **Phase 0 (Literature Review): CLOSED.** Both Literature Foundations written, converged, alignment chat concluded with `Summary.md`.
- **Phase 1 (Claim Sheet): CLOSED (Session 3).** Codex approved `Claim Sheet.md` rev. 2 (his Session 3). I executed the default-writer close-out: wrote `Accessible Claim Sheet.md`, created `director_requests.md`, flipped the Claim Sheet status header to PHASE 1 CLOSED, concluded the Phase 1 chat (renamed to `...Concluded.md` + `Summary.md`), and wrote `Progress Report Phase 1 Close.md`.
- **Phase 2 (Execution): OPEN.** Nothing built yet. The `venv` is still bare.

## What to do FIRST next session (Phase 2 build — my lane)

1. **Pinned dependency install** into the bare `venv`. ALWAYS `.\venv\Scripts\python.exe` / `.\venv\Scripts\pip.exe` — never bare. Write `requirements.txt` with pinned versions. License-check `nixio` (MIT-expected); record every dependency's license for the packet. Anticipated stack: `numpy scipy h5py nixio mne scikit-learn pandas matplotlib`; `pyriemann` later; `torch` (CUDA, 8 GB-sized) only at the CNN rung.
2. **NIX reader** (`utils/` module, per Standards: one purpose per script, `argparse` `required=True`, docstrings, loud failure). Produces aligned epochs (scalp + trial metadata; iEEG/units loaded lazily for the mechanism layer). **VALIDATE against the provided MATLAB loader / `NIX_File_Structure.pdf` as a stop-or-go correctness gate before any decoding runs.**
3. **Trial-count audit** — count maintenance-period trials per subject per load level. This **confirms or replaces the +0.075 success bar, and must happen BEFORE any model is run.** If counts make +0.075 honestly unattainable, open a NEW chat with Codex and agree a replacement bar before modeling — never after seeing results.
4. Surface the trial counts to Codex the moment the data layer can produce them; his lanes unblock then.

## The approved claim (so next session doesn't re-derive it)

**Headline (Slot 3, two coupled halves):** *Scalp EEG contains a subject-transferable signature of an intracranially-validated MTL working-memory state: in LOSO evaluation, scalp EEG alone predicts working-memory load above behavioral/timing/label-shuffle controls (half A), and the scalp signature is mechanistically tied to the MTL theta–alpha coupling the intracranial data shows tracks load (half B).*

- **Primary target = WM load (set size), binary high-vs-low (4 vs 6/8), decoded from the MAINTENANCE period.** Load is independent of any neural channel (avoids circularity). iEEG coupling + units = mechanism validation, NOT predicted target.
- **LOSO is the headline everywhere**; within-subject is diagnostic only. All model selection inside training subjects; held-out subject scored once; autocorrelation/window-leakage guard.
- **Controls:** label-shuffle, behavioral-only (**must exclude set size / any set-size-encoding variable**), timing-only, subject-identity, artifact.
- **Success bar (Slot 11, provisional pending trial-count audit):** mean LOSO balanced accuracy ≥0.075 over strongest non-signal control, ≥7/9 subjects above control, no single-subject removal below +0.04; subject-level sign-flip/permutation evidence (window-level may NOT substitute).
- **Mechanism coverage rule:** full deep-readout claim needs ≥5 subjects with adequate MTL coverage (Phase-2 coverage audit runs BEFORE mechanism analysis). <5 → "load decoding, mechanism too sparse" (named partial outcome, Slot 13). Decoding-without-mechanism is also a named partial outcome.
- **Model ladder (smallest-sufficient first):** regularized logistic/LDA → filter-bank covariance + shrinkage → Riemannian → EEGNet → foundation models (optional, later).
- **Pre-declared extension** = "mechanism-direct" (predict iEEG-defined coupling state from scalp). **Fast-follow** = Candidate B (scalp → MTL theta/alpha band-power time-course reconstruction).

## Ratified division of labor

- **Me (Claude):** data layer (NIX reader, alignment, LOSO harness, feature extraction) + primary load-decoding pipeline. Default writer for all 4 narrative docs.
- **Codex:** controls/stats spec + harness, subject-level uncertainty/permutation, verification-dashboard per-subject rendering. **Mechanism-validation analysis: Codex leads but co-owned** (rides my NIX reader/alignment exposing iEEG/unit inputs). Reviewer/approver for my docs.
- **Co-owned:** metrics, Reproducibility Packet. References reconciled jointly at Phase 2.

## Key substrate / environment facts (still current)

- Dataset `D:\Simultaneous EEG_LFP`: **37 NIX `.h5` files** in `data_nix/` + `code_MATLAB/` loader, `NIX_File_Structure.pdf`, `Subject_Characteristics.pdf`, `README.md`, `LICENSE`. 9 subjects, modified Sternberg verbal WM task. **License CC BY-SA 4.0** — commercial OK; **raw data NEVER committed to repo** (reference public G-Node DOI `10.12751/g-node.d76994`).
- NIX = HDF5 → `nixio` reads natively in Python; `h5py` fallback.
- `venv` at project root = Python 3.11.9, **BARE** (no libs). First Phase 2 task = pinned install.
- Compute: RTX 4070 Laptop, **8 GB VRAM**, 16 GB RAM. Favors compact models; 8 GB is a differentiator vs NeuroFlowNet (RTX 4080/16 GB).

## NeuroFlowNet (closest prior art — don't re-derive)

arXiv:2603.03354. Subject-specific (S1/S6/S9 only, 90/10 split), RTX 4080/16 GB, reconstructs MTL iEEG waveforms from scalp at 512 Hz. Alpha-FC relative error: full model 0.157 vs linear-regression 1.000. **Not LOSO.** Our 3 differentiators: subject-held-out generalization, 8 GB consumer hardware, deep-state validation over waveform mimicry.

## Process reminders specific to me

- I'm **default writer** for Claim Sheet, Accessible Claim Sheet, Technical Report, Accessible Piece (Codex reviews/approves). Both contribute to the Reproducibility Packet.
- **Keep `Claim Sheet.md` and `Accessible Claim Sheet.md` in sync** — any amendment to one updates the other the same session (drift = defect).
- **Progress report count:** I've written 2 (both phase-transition triggers: Phase 0 Close, Phase 1 Close — neither counts against the per-8-session cadence). My next *cadence* report is due at my **Session 8**; plus one at each future phase transition / approved amendment.
- **Cross-review each session:** read Codex's most recent unreviewed human report + the work it points to + relevant active chats; respond if warranted. (Session 3: reviewed Codex's HumanReport3 + his approval turn — clean, no pushback needed.)
- **Git note:** Codex's Session 3 push failed on a transient `.git/index.lock` permission error. It was gone by my session; I committed his Session 3 files alongside mine. If the lock error recurs, check `.git/index.lock` exists and is stale before removing.
- Chats live in `chats/Claude-Codex/`. Both Phase 0 alignment and Phase 1 Claim Sheet are **Concluded**. No active chats open right now — open a fresh one if the trial-count audit triggers a bar-replacement discussion.
- **Session lock:** this session runs under `.claude-session.lock` (created at start, deleted at end). Codex uses `.codex-session.lock`.
