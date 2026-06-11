# Summary of Only Necessary Context — Claude

**Last rewritten:** 2026-06-11 (Claude Session 2)
**Current phase:** Phase 1 — Sharpening (Claim Sheet drafted, under Codex review; NOT yet closed)

> Re-read `/Project Details/Project Details.md` and `AgentPrompt.md` in full at session start — do not duplicate them here. This file only holds what those don't.

## Where the project is right now

- **Phase 0 (Literature Review) is CLOSED.** Both agents wrote Literature Foundations, converged, alignment chat concluded with a `Summary.md`.
- **Phase 1 (Claim Sheet) is OPEN, near close.** I drafted `Claim Sheet.md` (root, all 15 slots), Codex reviewed it the same day and asked for 4 amendments before approving, I **applied all 4** (the sheet is now **rev. 2**) and ratified the labor split, and replied handing back for Codex's **explicit approval turn**. **Phase 1 closes when Codex posts that approval** — which he signalled is coming ("If you make those amendments, I expect to approve").

## What to do FIRST next session

1. **Check the Phase 1 chat** (`chats/Claude-Codex/Claim Sheet Phase 1/...Active.md`) for Codex's approval turn.
   - If Codex **approved**: run the Phase-1-close sequence below.
   - If Codex raised **new** points: address them in the chat first (he said he's not asking to change the high-level claim/structure/licensing/model ladder, so any new points should be minor).
2. **Phase-1-close sequence (once Codex approves):**
   - **Write the Accessible Claim Sheet** (my default-writer job) — plain-language companion to `Claim Sheet.md`, for the director, at the Accessible-Piece bar with credible-source links. Deferred until approval to avoid drift; the technical sheet is now stable enough that this should be straightforward.
   - **Create `director_requests.md` at project root**, first entry: *Claim Sheet ready for director review* (date; needed = Randy's review of `Claim Sheet.md` + Accessible Claim Sheet; why; blocked = nothing hard — Phase 2 proceeds regardless per framework).
   - Closing Phase 1 is a **phase transition → write `Progress Report Phase 1 Close.md`** (I offered to take it since the Accessible Claim Sheet is mine; confirm with Codex if he wrote the closing turn instead).
   - Then **conclude the Phase 1 chat** (rename to Concluded + `Summary.md`).
3. **Then Phase 2 begins:** pinned dependency install into the bare `venv`, then the NIX reader (validate against the MATLAB loader / `NIX_File_Structure.pdf` as a stop-or-go gate), then the **trial-count audit** (maintenance-period trials per subject per load level) which confirms or replaces the +0.075 success bar **before any model is run**.

## The four review asks — RESOLVED (Codex answered; amendments applied to rev. 2)

1. **Mechanism feasibility** → usable MTL subset unknown from text metadata alone; requires a **Phase-2 coverage audit before mechanism analysis**. Pre-declared **≥5-subject rule**: ≥5 with adequate MTL coverage → mechanism supports full claim; <5 → "load decoding, mechanism evidence too sparse," full claim forbidden even if subset looks positive. [Slots 9, 11, 13]
2. **Load target framing** → **classification first**, primary = **binary high-vs-low load, set size 4 vs 6/8** (Boran-style contrast, director-auditable). Secondary: 3-class set-size, ordinal/regression. [Slots 5, 7]
3. **Effect-size / permutation bar** → first-pass: **mean LOSO balanced accuracy ≥0.075 over strongest non-signal control, ≥7/9 subjects, no single-subject removal below +0.04**, subject-level sign-flip/permutation (no window-level substitute). **Replaceable only before any model runs**, if trial-count audit shows +0.075 honestly unattainable. [Slots 7, 11]
4. **Division of labor** → ratified with Codex's nuance: I own data layer + primary decoding; Codex owns controls/stats spec+harness + subject-level uncertainty + dashboard per-subject rendering; **mechanism analysis co-owned** (Codex leads, rides my NIX reader/alignment); metrics + packet co-owned. [labor section]
   - One more amendment Codex added beyond the 4 asks: **behavioral-only control must exclude set size / any label-encoding variable** (else it trivially predicts the target) — applied [Slot 7].

## The claim, as drafted (so next session doesn't re-derive it)

**Headline (Slot 3):** *Scalp EEG contains a subject-transferable signature of an intracranially-validated MTL working-memory state: in LOSO evaluation, scalp EEG alone predicts working-memory load above behavioral/timing/label-shuffle controls, and the scalp signature is mechanistically tied to the MTL theta–alpha coupling the intracranial data shows tracks load.*
- Two halves: (a) decoding headline, (b) mechanism. Decoding-without-mechanism is a **named partial outcome** (Slot 13), never reported as the full claim.
- **Primary target = WM load (set size)** — independent of any neural channel (avoids circularity). iEEG coupling + units = mechanism validation, not predicted target.
- **LOSO is the headline everywhere**; within-subject diagnostic only. Controls: label-shuffle, behavioral-only, timing-only, subject-identity, artifact + autocorrelation/window-leakage guard + "not carried by a single subject" robustness rule.
- Pre-declared extension = "mechanism-direct" variant (predict intracranially-defined coupling state from scalp-only features). Fast-follow = Candidate B (scalp→MTL theta/alpha band-power time-course reconstruction).
- Model ladder: regularized linear/LDA → filter-bank covariance → Riemannian → EEGNet → (foundation models optional, later). Smallest-sufficient first.

## Key substrate / environment facts (confirmed this session)

- Dataset `D:\Simultaneous EEG_LFP`: **37 NIX `.h5` files** in `data_nix/`, plus `code_MATLAB/` loader, `NIX_File_Structure.pdf`, `Subject_Characteristics.pdf`, `README.md`, `LICENSE`. 9 subjects, modified Sternberg verbal WM task. **License CC BY-SA 4.0** — commercial OK; raw data must NOT be committed to repo (see Claim Sheet Slot 4 for the full license policy).
- Data is **NIX-format HDF5** → `nixio` reads it natively in Python (license check pending — MIT-expected). `h5py` is a fallback.
- **`venv` exists at project root (Python 3.11.9) but is BARE** — no numpy/scipy/h5py/mne/scikit-learn/nixio/pandas/matplotlib/torch. First Phase 2 task = pinned install. ALWAYS use `.\venv\Scripts\python.exe` / `.\venv\Scripts\pip.exe`, never bare.
- Compute: RTX 4070 Laptop, **8 GB VRAM**, 16 GB RAM. Favors compact models; rules out from-scratch foundation models. 8 GB is a *differentiator* vs NeuroFlowNet (RTX 4080/16 GB).

## NeuroFlowNet facts (closest prior art — Codex extracted, don't re-derive)

arXiv:2603.03354. Subject-specific (S1/S6/S9 only, 90/10 trial split), RTX 4080/16 GB, reconstructs MTL iEEG waveforms from scalp at 512 Hz. Alpha-FC relative error: full model mean 0.157 (best) vs linear-regression 1.000. **Not a LOSO benchmark.** Our 3 differentiators: subject-held-out generalization, 8 GB consumer hardware, deep-state validation over waveform mimicry.

## Process reminders specific to me

- I'm the **default writer** for Claim Sheet, Accessible Claim Sheet, Technical Report, Accessible Piece (Codex reviews/approves). Both contribute to the Reproducibility Packet.
- **Progress report count:** I've written 1 so far (Phase 0 Close, a transition trigger — does NOT count against the per-8-session cadence). My next *cadence* progress report is due at my **Session 8**; plus one at each future phase transition / approved amendment. (Phase 1 close will trigger one next.)
- **Cross-review each session:** read the most recent unreviewed human report from Codex + the work it points to + relevant active chats, and respond if warranted. (This session I reviewed Codex's HumanReport1 + Literature Foundation + chat reply.)
- Chats live in `chats/Claude-Codex/`. Phase 0 alignment = **Concluded**. Active = **Claim Sheet Phase 1**.
