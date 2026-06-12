# Summary of Only Necessary Context — Claude

**Last rewritten:** 2026-06-12 (Claude Session 10)
**Current phase:** **Phase 3 — Deliverables.** Analysis is COMPLETE and settled (Amendment 1 ratified S8, final-wording-approved by Codex S10). Two-part result locked. Of the three required deliverables: **Technical Report = drafted + compiling, [P2]+[P3] closed, only [P1] figures left; Accessible Piece = WRITTEN this session (S10), pending Codex approval; Reproducibility Packet = NOT STARTED (the last big lift).**

> Re-read `/Project Details/Project Details.md` and `AgentPrompt.md` in full at session start — do not duplicate them here. This file only holds what those don't.

## #1 PRIORITY NEXT SESSION

1. **Reproducibility Packet** (co-owned) — the last unbuilt required deliverable; biggest remaining task. Needs: top-level README walking an outside reader from the public G-Node DOI download (`10.12751/g-node.d76994`, CC BY-SA 4.0) through reproducing **every** number, with the **verification dashboard** (`scripts/render_verification_dashboard.py`, HTML) as the reader's first way in. Its OWN `requirements.txt` (pin versions) + OWN `.gitignore` + a code license (MIT or Apache-2.0, pick at assembly — both commercial-OK). **No raw data in repo.** README must NOT mention local paths, the Collaboration Station, or session history — it's for a cold outside reader. Suggested location `deliverables/reproducibility_packet/`.
2. **Technical Report [P1]** — insert verification-dashboard figures at ≥300 DPI. Dashboard renders as **HTML**, so this needs a render-to-image step (headless browser screenshot, or re-plot the key panels in matplotlib at 300 DPI). Co-owned with Codex; coordination flagged in the *Accessible Piece Review* chat. Numeric tables already carry all load-bearing results, so figures augment, not replace.
3. **Codex's review** of the Accessible Piece + his [P3] confirmation — pending in the *Accessible Piece Review* active chat. Check for his reply; if he requests changes to the Accessible Piece, apply forward.

When Phase 2 / Phase 3 formally closes, **whoever closes the transition writes a Progress Report** (extra trigger). My next *cadence* progress report is at my Session 16.

## THE TWO-PART RESULT (load-bearing numbers — locked)

**Part A — clean NEGATIVE (Slot 12 activated).** 8-ch common-montage LOSO load decoding does not beat strongest control by the pre-declared +0.075. Mean LOSO balanced acc (chance 0.50): logistic 0.560 · covariance 0.559 · tangent 0.558 (+rc 0.552) · MDM 0.533 (+rc 0.545) · **EEGNet 0.616**. Strongest non-signal control = behavioral-only **0.593**, almost entirely `previous_trial_correct` (REAL pre-declared task-schedule channel: incorrect→forced set-size-4 next; prev_correct=0→high-load 2/130=0.015; =1→1021/1523=0.670; prev-correct alone 0.596, 9/9; RT/correctness/trial/session each 0.500). **EEGNet is the ONLY rung above 0.593 on the mean but FAILS the bar:** +0.023 (need +0.075), 5/9 (need 7/9), min-leave-one-out −0.001 (S04 alone carries it: +0.218 vs next +0.045; need +0.04), bootstrap CI [−0.022,+0.081] crosses 0, sign-flip p=0.262. id_diag=1.000 every fold (covariance space perfectly subject-separable). Brain-only 6-ch EEGNet 0.623 ≈ all-ch → A1/A2 reference check passes. **Ceiling = 8-ch common montage + cross-subject transfer, NOT model class.** Foundation-model rung NOT run (ladder declared exhausted).

**Part B — EXPLORATORY, NOT validated (Slot 13 activated).** Intracranial MTL substrate real: theta−alpha load effect z=0.143, 7/9, p2=0.0156 (theta alone z=0.120 5/9 p2=0.32; alpha z=0.025 5/9 p2=0.81). EEGNet score couples RAW (theta +0.078 6/9; alpha +0.057 6/9; **theta−alpha +0.068 7/9 p2=0.0508**) where linear/tangent ≈−0.01. **Collapses under residualization:** load +0.050 (p2=0.13) → schedule +0.011 (p2=0.75) → behavior +0.013 (p2=0.71). **Codex's confirmatory gate (S11) FAILED clearly:** schedule-residualized metric, required +mean & ≥7/9 & sign-flip p≤0.05 & all LOO>0 → got mean +0.011, 4/9, p=0.746, min LOO −0.010. At n=9 can't disambiguate real load-linked shared MTL state vs schedule-linked correlate → report exploratory/inconclusive. **Part B is a named next-signal-to-chase, not a finding.**

## What I did Session 10

1. **Wrote the Accessible Piece** (`deliverables/accessible_piece/Accessible Piece.md`) — the last unwritten required deliverable. Full plain-language arc: electrical-fMRI dream → why deep readout is hard → MTL↔cortex coupling as the hope → simultaneous Boran dataset as ground truth → first-rung question → 3 honesty safeguards (LOSO, the prev-trial schedule control, pre-declared bars) → Part A clean negative + *why* → Part B exploratory lead that didn't survive (cites Codex's failed gate) → why a clean negative is a real contribution → next signal. Credible-source links for every non-obvious term. Strictly non-promotional; Part B kept as "lead, not proven."
2. **Closed [P3]** — joint bibliography reconciliation. All 9 `\cite` keys present in `references.bib` w/ verified DOIs; cross-checked both agents' `references.md`; uncited context sources intentionally left in per-agent files (plain style prints only cited works); fixed `neuroflownet2026` author list + DOI; updated `.bib` header + technical_report `README.md`. **Rebuilt report: compiles clean, no undefined refs, 272 KB PDF.**
3. Opened `chats/Claude-Codex/Accessible Piece Review/` (ACTIVE) handing Codex the Accessible Piece + asking him to confirm [P3].
4. Cross-review: read Codex HumanReport11 + his S11 work (confirmatory gate, dashboard update). Agreed; built Part B framing on it. No corrections.
5. **Committed Codex's completed S11 work** (he still can't push) bundled with mine.

## Division of labor (ratified)

- **Me (Claude):** data ✓ + features ✓ + LOSO ✓ + decoding ladder rungs 1–4 ✓ + mechanism co-owned (fed decoder preds ✓). **Default writer for all 4 narrative docs** — Claim Sheet ✓, Accessible Claim Sheet ✓, Technical Report (draft ✓, [P1] figs left), **Accessible Piece ✓ (S10)**.
- **Codex:** controls/stats/harness ✓ + behavioral ablation ✓ + mechanism (leads) ✓ + Part B confirmatory gate ✓ (S11, failed) + residual probe ✓ + dashboard. Reviewer/approver for my docs.
- **Co-owned & remaining:** **Reproducibility Packet** (not started), verification dashboard, [P1] report figures.

## Process reminders specific to me

- **Progress reports:** written 4 (Phase 0 Close, Phase 1 Close, Session 8 cadence, Amendment 1). Next **cadence** at my Session 16. Plus one at each future phase transition / approved amendment (whoever closes it writes it). **A formal Phase 2-close or Phase 3-close is a report trigger.**
- **Cross-review done S10:** read Codex HumanReport11 (covers his S11; older subsumed). Agreed, no correction; corrections propagate forward.
- **Amendment status:** Amendment 1 RATIFIED + on BOTH sheets + Codex final-approved (S10). Next amendment (if any) = append-only protocol. I did NOT touch the Claim/Accessible Claim Sheets this session (nothing changed direction).
- **GIT PROTOCOL (Randy, S8):** Codex still can't push (`.git/index.lock` permission error — confirmed not stale in his S11 report; GitHub also unreachable from his sandbox). I push his COMPLETED working-tree files alongside mine. Message format **"Claude Session N; Codex Session M"** — ONLY when Codex's session is COMPLETE; never bundle an unfinished one. **This session's push = "Claude Session 10; Codex Session 11"** (his S11 complete, `.codex-session.lock` absent at my start).
- **Session lock:** `.claude-session.lock` (create at start, delete at end). Codex uses `.codex-session.lock` — PER-AGENT (parallel by design). Stale lock from a crashed session is safe to clear. Scheduled task `dandelion-engineering-N` drives my sessions via `AgentPrompt.md`.
- **LaTeX IS installed on this machine** (MiKTeX: pdflatex/bibtex on PATH). Report builds clean here. **Note: Codex's sandbox MiKTeX is broken (missing formats.ini) — if he reports a build failure it's his env, not the source; I verify builds on my side.** Build artifacts gitignored.
- **torch is NOT installed and should NOT be** (EEGNet is pure NumPy). pyriemann also not installed. If either added, pin in requirements.txt (both BSD/commercial-OK).
- **Outputs are gitignored** (`/outputs/`, rebuildable). `deliverables/` is TRACKED. **Bash tool quirk: use forward-slash paths** — backslashes get stripped. Also: `cd` into a subdir persists in the Bash shell across calls and confuses relative git paths — `cd` back to project root or use absolute paths when checking git state.
