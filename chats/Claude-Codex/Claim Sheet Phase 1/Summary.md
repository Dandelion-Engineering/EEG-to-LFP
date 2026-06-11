# Summary — Claim Sheet Phase 1 Review (Concluded)

**Participants:** Claude, Codex
**Date range:** 2026-06-11 (opened Claude Session 2, 07:02 PDT → concluded Claude Session 3, 08:42 PDT)
**Outcome:** Technical Claim Sheet **approved** by both agents (rev. 2); labor split ratified; Phase 1 **closed**; Phase 2 open.

## What this chat did

This was the Phase 1 review thread. Claude (default writer) drafted the technical `Claim Sheet.md`; Codex (reviewer/approver) reviewed it, required four amendments, Claude applied all four (→ rev. 2), and Codex gave explicit approval. Then Claude executed the default-writer close-out and concluded the chat.

## The four amendments Codex required (all applied in rev. 2)

1. **Behavioral-only control must exclude the label.** Slot 7 now explicitly bars set size / any set-size-encoding variable from the behavioral-only control (else it trivially predicts the load target). Allowed non-signal covariates named: response time, correctness, match/mismatch, session, trial order, timing.
2. **Headline epoch fixed to maintenance.** Slots 5/7 — decode load during the *maintenance* period, not encoding (an encoding-period model could win on transient sensory stimulus-load cues rather than the maintained MTL state). Encoding/recall demoted to secondary diagnostics.
3. **Concrete success thresholds.** Slots 5/7/11 — primary = binary high-vs-low load (set size 4 vs 6/8), metric = LOSO balanced accuracy during maintenance, anchored as improvement over the strongest non-signal control. Bar: **mean ≥0.075 above control, ≥7/9 held-out subjects above control, no single-subject removal dropping mean improvement below 0.04**, subject-level sign-flip/permutation evidence (window-level permutation may not substitute). Replaceable **only before any model runs** if a Phase-2 trial-count audit shows +0.075 is honestly unattainable.
4. **Mechanism coverage downgrade rule.** Slots 9/11/13 — a Phase-2 MTL-coverage audit runs *before* mechanism analysis; the full deep-readout claim requires **≥5 subjects** with adequate MTL coverage; <5 → "load decoding with mechanism evidence too sparse," full claim forbidden even if the available subset looks positive.

## Ratified division of labor

- **Claude:** data layer (NIX reader, event/epoch alignment, LOSO harness, feature extraction) + primary load-decoding pipeline.
- **Codex:** controls/statistics spec + harness (label-shuffle, behavioral-only [target-excluded], timing-only, autocorrelation guard, subject-level permutation/uncertainty) + verification-dashboard per-subject rendering.
- **Co-owned:** mechanism-validation analysis (Codex leads; rides Claude's NIX reader/alignment exposing iEEG/unit inputs), metrics, Reproducibility Packet.
- Writing convention: Claude drafts the four narrative docs; Codex reviews/approves.

## Close-out actions (Claude Session 3)

- `Accessible Claim Sheet.md` written (plain-language companion, in sync with the technical sheet).
- `director_requests.md` created, Request 1 = *Claim Sheet ready for director review* (non-blocking).
- `Claim Sheet.md` status header → PHASE 1 CLOSED / Phase 2 open.
- `Progress Report Phase 1 Close.md` written (phase-transition trigger, fell to Claude as closing-turn writer).

## Context to carry into Phase 2

- **The +0.075 bar is provisional pending the trial-count audit.** First real Phase 2 task (Claude's lane): pinned dependency install into the bare `venv`, then the NIX reader validated against the MATLAB loader / `NIX_File_Structure.pdf` as a stop-or-go gate, then count maintenance-period trials per subject per load level. If those counts make +0.075 unattainable for honest reasons, a replacement bar is proposed in a *new* chat **before any model is run**.
- **Codex should not start Phase 2 implementation until the data layer exposes aligned epochs + iEEG/unit inputs** — his lanes (controls/stats harness, mechanism lead, dashboard) unblock at that point.
- Open director dependency: Randy's review of the Claim Sheet (logged in `director_requests.md`), handled as the first amendment cycle whenever it lands. Non-blocking.
