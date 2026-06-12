# Summary of Only Necessary Context — Claude

**Last rewritten:** 2026-06-12 (Claude Session 9)
**Current phase:** **Phase 3 — Deliverables (OPEN on the writing side), inside a Phase 2 project whose analysis is essentially settled.** Decoding ladder COMPLETE + EXHAUSTED (rungs 1–4). **Amendment 1 RATIFIED (S8) and final-wording-APPROVED by Codex (S10):** claim re-pointed to a two-part result [A: bounded negative decoding; B: exploratory MTL coupling, NOT validated]. The `Riemannian Ladder Verdict` chat is **CONCLUDED** (Summary.md written, S9). **Technical Report first draft is IN and compiles** (`deliverables/technical_report/main.tex`).

> Re-read `/Project Details/Project Details.md` and `AgentPrompt.md` in full at session start — do not duplicate them here. This file only holds what those don't.

## #1 PRIORITY NEXT SESSION

The project has a concludable result; remaining work is Phase 3 deliverables (+ one optional analysis). In rough priority:
1. **Accessible Piece** (MY lane, default writer) — same project for a non-technical reader; not started. Reuse language from `Progress Report Amendment 1 …` and the Technical Report. Lives wherever I put it (suggest `deliverables/accessible_piece/`).
2. **Reproducibility Packet** (co-owned) — top-level README walking an outside reader from the public G-Node DOI download through reproducing every result; its OWN `requirements.txt` + `.gitignore` + code license (MIT/Apache-2.0, set at assembly); the **verification dashboard** (`scripts/render_verification_dashboard.py` exists) as the reader's first way in. No raw data in repo. Suggest `deliverables/reproducibility_packet/`.
3. **Technical Report open items** (in `deliverables/technical_report/`, flagged inline + in its README): **[P1]** insert dashboard figures ≥300 DPI; **[P2]** Part B confirmatory-test result slot (§5.2, waits on Codex); **[P3]** final joint references reconciliation (my + Codex `references.md`).
4. **Part B confirmatory coupling test** — **Codex's lane** (don't write his script). Band/metric fixed a priori (MTL theta−alpha diff) + residualization/robustness required, NOT raw p2<0.05 on the already-inspected metric. I feed decoder scores. The Technical Report absorbs the outcome forward either way.

When Phase 2 formally closes / Phase 3 formally closes, **whoever closes the transition writes a Progress Report** (that's an additional trigger; my next *cadence* report is at my Session 16).

## THE DECODING VERDICT (COMPLETE — load-bearing numbers)

Mean LOSO balanced acc, headline 8-ch montage (chance 0.50): logistic 0.560 · covariance 0.559 · tangent 0.558 (+rc 0.552) · MDM 0.533 (+rc 0.545) · **EEGNet 0.616**. Strongest non-signal control = behavioral-only **0.593**, which is almost entirely `previous_trial_correct` (REAL predeclared task-schedule channel: incorrect→forced set-size-4 next trial; prev_correct=0→high-load 2/130=0.015; =1→1021/1523=0.670; Codex S7 ablation: RT/correctness/trial/session each 0.500). **EEGNet is the ONLY rung to beat 0.593 on the mean but FAILS the bar:** improvement +0.023 (need +0.075), 5/9 (need 7/9), min-leave-one-out −0.001 (S04 alone carries it: +0.218 vs next +0.045; need +0.04), bootstrap CI [−0.022,+0.081] crosses 0, sign-flip p1=0.2617. `id_diag=1.000` every fold (covariance space perfectly subject-separable). Brain-only 6-ch EEGNet 0.623 ≈ all-ch 0.616 → A1/A2 reference check passes. **Ceiling = 8-ch common montage + cross-subject transfer, NOT model class.** Optional foundation-model rung NOT run (ladder declared exhausted).

## THE COUPLING RESULT (Part B — exploratory, NOT validated)

Intracranial MTL substrate real: theta−alpha load effect z=0.143, 7/9, p2=0.0156 (theta alone z=0.120 5/9 p2=0.32; alpha z=0.025 5/9 p2=0.81). EEGNet score couples to it RAW (theta +0.078 6/9 p2=0.16; alpha +0.057 6/9 p2=0.29; **theta−alpha +0.068 7/9 p2=0.0508**) where linear/tangent showed ≈−0.01. **But collapses under residualization:** load 0.050 (p2=0.13) → schedule 0.011 (p2=0.75) → behavior 0.013 (p2=0.71). At n=9 can't disambiguate real load-linked shared MTL state vs schedule-linked correlate → report as exploratory/inconclusive.

## What I did Session 9

1. Cross-review: read Codex HumanReport10 + `summarize_phase2_amendment_evidence.py` (agree; cite the script not the ignored output). No corrections — built forward.
2. **Opened Phase 3 / drafted the Technical Report:** `deliverables/technical_report/` → `main.tex` (complete, **compiles** pdflatex+bibtex, 10 pp, no undefined refs) + `references.bib` + `README.md`. Built entirely around the two-part result with full numeric tables. Left 3 marked open items [P1/P2/P3].
3. **Concluded `Riemannian Ladder Verdict` chat:** appended my S9 closing turn, renamed Active→Concluded, wrote `Summary.md`.
4. Spelled out amendment-log approval provenance (S9 direction/language, S10 final wording) in `Claim Sheet.md` per Codex's bookkeeping note.
5. Removed stray empty `outputsdecoding/` dir.
6. **Committed Codex's completed S9–S10 work** (he still can't push) bundled with mine.

## The amended claim (current contract)

Read `Claim Sheet.md` Slots 1–15 as the original recorded turn; **current direction = those slots AS MODIFIED BY Amendment 1** at the bottom. Part A: 8-ch common-montage LOSO load decoding does not beat strongest control by +0.075 across the full ladder (clean failure, Slot 12 activated). Part B: MTL theta−alpha coupling lead, exploratory/inconclusive (Slot 13 activated), confirmatory test prospective. Slot 11 bar held fixed + unmet (not weakened). Slot 5 extensions (mechanism-direct, Candidate B) NOT run (gated on primary success). Accessible Claim Sheet synced.

## Division of labor (ratified)

- **Me (Claude):** data ✓ + features ✓ + LOSO ✓ + decoding ladder rungs 1–4 ✓ + mechanism co-owned (feed decoder preds to Codex's probe ✓). **Default writer for all 4 narrative docs** — Claim Sheet ✓, Accessible Claim Sheet ✓, **Technical Report (draft started S9)**, Accessible Piece (not started).
- **Codex:** controls/stats/harness ✓ + behavioral ablation ✓ + mechanism (leads) ✓ + **owns Part B confirmatory coupling test** + residual probe ✓. Reviewer/approver for my docs.
- **Co-owned:** metrics, mechanism, Reproducibility Packet, verification dashboard. References reconciled jointly (pending — item [P3]).

## Process reminders specific to me

- **Progress reports:** written 4 (Phase 0 Close, Phase 1 Close, Session 8 cadence, Amendment 1). Next **cadence** at my Session 16. Plus one at each future phase transition / approved amendment (whoever closes it writes it). **Watch: a formal Phase 2-close or Phase 3-close is a report trigger.**
- **Cross-review done S9:** read Codex HumanReport10 (covers S9+S10; older reports subsumed) + his evidence summarizer. Agreed, no correction; corrections propagate forward.
- **Amendment status:** Amendment 1 RATIFIED + written to BOTH sheets + Codex final-approved (S10). Original slots preserved as recorded turn. Next amendment (if any) = same append-only protocol.
- **GIT PROTOCOL (Randy, S8):** Codex still can't push (his `.git/index.lock` permission error — confirmed not stale in his S10 report). I push his COMPLETED working-tree files alongside mine. Message format **"Claude Session N; Codex Session M"** — ONLY when Codex's session is COMPLETE; never bundle an unfinished Codex session. **This session's push = "Claude Session 9; Codex Session 10"** (his S9+S10 both complete, `.codex-session.lock` absent at my start). The S8 pending-commit backlog is now CLEARED by this push.
- **Session lock:** `.claude-session.lock` (create at start, delete at end). Codex uses `.codex-session.lock` — PER-AGENT (parallel by design). Stale lock from a crashed session is safe to clear. Scheduled task `dandelion-engineering-N` drives my sessions via `AgentPrompt.md`.
- **LaTeX IS installed** (MiKTeX: pdflatex/bibtex/latexmk/xelatex on PATH). Technical Report builds clean. Build artifacts gitignored (`*.pdf/*.aux/*.log/*.bbl/*.blg/*.out/*.toc`).
- **torch is NOT installed and should NOT be installed** (EEGNet is pure NumPy). pyriemann also not installed. If either added, pin in requirements.txt (both BSD/commercial-OK).
- **Outputs are gitignored** (`/outputs/`, rebuildable). `deliverables/` is TRACKED. **Bash tool quirk: use forward-slash paths** — backslashes get stripped (caused the `outputsdecoding` stray dir; removed S9).
