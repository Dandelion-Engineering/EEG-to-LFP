# Summary of Only Necessary Context — Claude

**Last rewritten:** 2026-06-12 (Claude Session 12)
**Current phase:** **Phase 3 — Deliverables, awaiting final close.** Analysis COMPLETE and settled (Amendment 1 ratified, final wording approved). **All three required deliverables EXIST and are validated:** Technical Report (drafted; [P1]/[P2]/[P3] closed; **source stamped APPROVED by Codex Session 13**), Accessible Piece (written S10, **APPROVED by Codex S12**), Reproducibility Packet (built S11; **clean-room end-to-end reproduction PASSED this session S12** — see below; **pending only Codex's explicit approval**). Phase 3 closes when all three are explicitly approved by BOTH agents.

> Re-read `/Project Details/Project Details.md` and `AgentPrompt.md` in full at session start — do not duplicate them here. This file only holds what those don't.

## #1 PRIORITY NEXT SESSION

1. **Check the *Reproducibility Packet Review* active chat** (`chats/Claude-Codex/Reproducibility Packet Review/`). I appended my S12 clean-room validation report there. If Codex has replied and **approved the packet** → with the Accessible Piece (approved) and Technical Report (Codex stamped source approved S13) all explicitly approved by both agents, **Phase 3 is CLOSEABLE.** Whoever writes the closing turn writes a **Progress Report Phase 3 Close** (extra report trigger) and the project is COMPLETE as scoped. Apply any packet change requests forward first.
2. **If Phase 3 is already complete when you initialize:** per Project Details, do NOT invent new work. A session initialized into a completed project ends without adding work (no human report, no summary rewrite) UNLESS the director gives an explicit signal to continue. Check `director_requests.md` and recent chats for any such signal first.
3. **The clean-room validation gap is now CLOSED** (was priority #3 last session). No remaining technical blockers to packet approval.

My next *cadence* progress report is at my **Session 16**. A Phase-3-close is an additional report trigger (whoever closes it writes it).

## WHAT I DID THIS SESSION (S12) — clean-room reproduction

Ran the FULL packet pipeline exactly per the README Section 5, from raw NIX → dashboard, into a throwaway `outputs_cleanroom/` (kept separate from canonical `outputs/` because Codex was running a concurrent session). All 11 steps: NIX reader gate (20/20) → metadata → audit (montage `A1 A2 C3 C4 F3 F4 O1 O2`, 1683 trials, 144 exclusions) → features → LOSO folds → logistic → **EEGNet all 9 folds (~2 hr CPU, elapsed 7202s)** → controls + behavioral ablation → statistics → MTL coverage/bandpower/residual/gate → amendment evidence → dashboard render.

**RESULT: every load-bearing number reproduced EXACTLY; dashboard byte-identical (SHA-256 `383048fc1d590dde862070fdf46203510e4ddc36678510ac0431d3197565d123`) to shipped + canonical copies.** EEGNet mean 0.616, +0.023, 5/9, min-LOO −0.001, success=false; logistic 0.560; Part B raw +0.068/7-9/p2 0.0508, load-resid +0.050, schedule-resid gate +0.011/4-9/p2 0.746/gate_passed=false. Standards "runs end-to-end on a fresh environment" clause now satisfied by an actual fresh run. Deleted `outputs_cleanroom/` after recording (rebuildable scratch; Codex independently added it to `.gitignore` in his S13). README Section-5 ordering confirmed correct; `build_features` emits BOTH `feature_metadata.csv` + `.parquet` so the 5.7 `.csv` reference resolves.

## THE TWO-PART RESULT (load-bearing numbers — locked, now reproduced byte-identically)

**Part A — clean NEGATIVE (Slot 12 activated).** 8-ch common-montage LOSO load decoding does not beat strongest control by pre-declared +0.075. Mean LOSO balanced acc (chance 0.50): logistic 0.560 · covariance 0.559 · tangent 0.558 (+rc 0.552) · MDM 0.533 (+rc 0.545) · **EEGNet 0.616**. Strongest non-signal control = behavioral-only **0.593**, almost entirely `previous_trial_correct` (REAL pre-declared task-schedule channel: incorrect→forced set-size-4 next). **EEGNet is the ONLY rung above 0.593 on the mean but FAILS the bar:** +0.023 (need +0.075), 5/9 (need 7/9), min-LOO −0.001 (S04 alone carries it: 0.787), bootstrap CI [−0.022,+0.081] crosses 0, sign-flip p=0.523. Brain-only 6-ch EEGNet ≈ all-ch → reference-artifact check passes. **Ceiling = 8-ch common montage + cross-subject transfer, NOT model class.**

**Part B — EXPLORATORY, NOT validated (Slot 13 activated).** Intracranial MTL substrate real: theta−alpha load effect. EEGNet score couples RAW (theta−alpha +0.068, 7/9, p2=0.0508) where linear/tangent ≈−0.01. **Collapses under residualization:** load +0.050 (p2=0.13) → schedule +0.011 (p2=0.75) → behavior +0.013 (p2=0.71). **Codex's confirmatory gate FAILED clearly:** schedule-residualized, required +mean & ≥7/9 & sign-flip p≤0.05 & all LOO>0 → got +0.011, 4/9, p=0.746, min LOO −0.010. At n=9 can't disambiguate real load-linked shared MTL state vs schedule-linked correlate → reported exploratory/inconclusive.

## Division of labor (ratified)

- **Me (Claude):** data ✓ + features ✓ + LOSO ✓ + decoding rungs 1–4 ✓ + mechanism co-owned (fed decoder preds ✓). **Default writer for all 4 narrative docs** — Claim Sheet ✓, Accessible Claim Sheet ✓, Technical Report (draft ✓, all P-items closed), Accessible Piece ✓ (approved). Built Reproducibility Packet S11 + **clean-room validated it S12** (co-owned).
- **Codex:** controls/stats/harness ✓ + behavioral ablation ✓ + mechanism leads ✓ + Part B confirmatory gate ✓ (failed) + residual probe ✓ + dashboard ✓ + Technical Report [P1] figures ✓ (S12) + **report source approval ✓ (S13)**. Reviewer/approver for my docs + the packet.
- **Co-owned remaining:** Reproducibility Packet approval (Codex's side — last Phase-3 gate).

## Process reminders specific to me

- **Progress reports:** written 4 (Phase 0 Close, Phase 1 Close, Session 8 cadence, Amendment 1). Next **cadence** at my Session 16. Plus one at each future phase transition / approved amendment (whoever closes it writes it). **A Phase-3-close is a report trigger.** S12 was NOT a report trigger (not a cadence session, no phase transition closed).
- **Cross-review done S12:** Codex's latest FINISHED report at my session start was HumanReport12 (already reviewed S11). His S13 was in-progress (lock present), HumanReport13 untracked/unfinished — not yet reviewable; I observed his working-tree changes (report-source approval, `.gitignore` += `/outputs_cleanroom/`) but did not commit them. Review HumanReport13 next session once his session is complete.
- **Amendment status:** Amendment 1 RATIFIED + on BOTH sheets + Codex final-approved. Next amendment (if any) = append-only protocol. Did NOT touch Claim/Accessible Claim Sheets S12.
- **GIT PROTOCOL (Randy, S8):** Codex still can't push (`.git/index.lock` permission error; GitHub unreachable from his sandbox). I push his COMPLETED working-tree files alongside mine, message **"Claude Session N; Codex Session M"** — ONLY when Codex's session is COMPLETE (`.codex-session.lock` ABSENT at my start). **S12 EXCEPTION: Codex's lock was PRESENT at my start (his S13 active), so I committed ONLY my own files with message "Claude Session 12" and left his in-progress changes (`.gitignore`, `deliverables/technical_report/*`, `agents/Codex/*`, `HumanReport13.md`) UNCOMMITTED for him.** Next session, if his S13 is complete, his files can be pushed.
- **Session lock:** `.claude-session.lock` (create at start, delete at end). Codex uses `.codex-session.lock` — PER-AGENT. Stale lock from a crashed session is safe to clear. Scheduled task `dandelion-engineering-N` drives my sessions via `AgentPrompt.md`.
- **LaTeX IS installed on my machine** (MiKTeX: pdflatex/bibtex). Report builds clean here. **Codex's sandbox MiKTeX is broken (missing formats.ini + lock-path perms)** — his PDF build failures are env, not source; I verify builds on my side. Build artifacts gitignored.
- **torch is NOT installed and should NOT be** (EEGNet is pure NumPy). pyriemann also not installed. Packet `requirements.txt` is framework-free by design.
- **Outputs are gitignored** (`/outputs/`, `/outputs_cleanroom/`, rebuildable). `deliverables/` is TRACKED (incl. `reproducibility_packet/`; shipped `verification_dashboard.html` is tracked, packet `.gitignore` only ignores suffixed `verification_dashboard_*.html`). **Bash tool quirk: use forward-slash paths.** `cd` into a subdir persists in the Bash shell — use absolute paths or `cd` back to root when checking git state.
- **Python invocation:** always `.\venv\Scripts\python.exe` / `.\venv\Scripts\pip.exe` (never bare). On PowerShell tool, `& $py script.py ...`. On Bash tool: `PY=./venv/Scripts/python.exe`.
- **Full clean-room reproduction cost:** ~2 hr wall (EEGNet 9 folds dominate at 7202s; everything else seconds-to-minutes). Run EEGNet in background; downstream stages are quick. No memory pressure post disk-clear.
