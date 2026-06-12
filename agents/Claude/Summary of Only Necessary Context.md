# Summary of Only Necessary Context — Claude

**Last rewritten:** 2026-06-12 (Claude Session 11)
**Current phase:** **Phase 3 — Deliverables, nearly closed.** Analysis is COMPLETE and settled (Amendment 1 ratified, final wording approved). **All three required deliverables now EXIST:** Technical Report (drafted; [P1]/[P2]/[P3] all closed; awaiting Codex's explicit final-approval stamp — README still says DRAFT), Accessible Piece (written S10, **APPROVED by Codex S12**), Reproducibility Packet (**built this session, S11**, pending Codex review). Phase 3 closes when all three are explicitly approved by BOTH agents.

> Re-read `/Project Details/Project Details.md` and `AgentPrompt.md` in full at session start — do not duplicate them here. This file only holds what those don't.

## #1 PRIORITY NEXT SESSION

1. **Check the *Reproducibility Packet Review* active chat** (`chats/Claude-Codex/Reproducibility Packet Review/`). I opened it S11 handing Codex the packet + asking him for (a) packet approval and (b) the Technical Report's explicit final-deliverable approval. If he replied: apply any requested packet changes forward; if he approved both AND the Accessible Piece is already approved, **Phase 3 is closeable** — whoever writes the closing turn writes a **Progress Report Phase 3 Close** (extra report trigger) and the project is then COMPLETE as scoped.
2. **If Phase 3 is complete:** per Project Details, do NOT invent new work. A session initialized into a completed project should end without adding work (no human report, no summary rewrite) UNLESS the director gives an explicit signal to continue. Check `director_requests.md` and recent chats for any such signal first.
3. **Open validation gap on the packet:** a clean-room end-to-end reproduction run (NIX read → feature build → EEGNet LOSO → controls → stats → mechanism → dashboard) to fully satisfy the Standards "validate on a fresh environment" clause. I validated only the dataset-free final-stage commands this session (they reproduce exactly; rendered dashboard is byte-identical to the shipped copy). The slow/dataset-dependent stages weren't re-run. Coordinate with Codex on who runs it before declaring the packet bulletproof.

My next *cadence* progress report is at my **Session 16**. A Phase-3-close is an additional report trigger (whoever closes it writes it).

## THE TWO-PART RESULT (load-bearing numbers — locked)

**Part A — clean NEGATIVE (Slot 12 activated).** 8-ch common-montage LOSO load decoding does not beat strongest control by the pre-declared +0.075. Mean LOSO balanced acc (chance 0.50): logistic 0.560 · covariance 0.559 · tangent 0.558 (+rc 0.552) · MDM 0.533 (+rc 0.545) · **EEGNet 0.616**. Strongest non-signal control = behavioral-only **0.593**, almost entirely `previous_trial_correct` (REAL pre-declared task-schedule channel: incorrect→forced set-size-4 next; prev_correct=0→high-load 2/130=0.015; =1→1021/1523=0.670; prev-correct alone 0.596). **EEGNet is the ONLY rung above 0.593 on the mean but FAILS the bar:** +0.023 (need +0.075), 5/9 (need 7/9), min-leave-one-out −0.001 (S04 alone carries it: +0.218 vs next +0.045; need +0.04), bootstrap CI [−0.022,+0.081] crosses 0, sign-flip p=0.262. Brain-only 6-ch EEGNet 0.623 ≈ all-ch → reference-artifact check passes. **Ceiling = 8-ch common montage + cross-subject transfer, NOT model class.**

**Part B — EXPLORATORY, NOT validated (Slot 13 activated).** Intracranial MTL substrate real: theta−alpha load effect z=0.143, 7/9, p2=0.0156. EEGNet score couples RAW (theta−alpha +0.068, 7/9, p2=0.0508) where linear/tangent ≈−0.01. **Collapses under residualization:** load +0.050 (p2=0.13) → schedule +0.011 (p2=0.75) → behavior +0.013 (p2=0.71). **Codex's confirmatory gate FAILED clearly:** schedule-residualized, required +mean & ≥7/9 & sign-flip p≤0.05 & all LOO>0 → got +0.011, 4/9, p=0.746, min LOO −0.010. At n=9 can't disambiguate real load-linked shared MTL state vs schedule-linked correlate → reported exploratory/inconclusive.

## Reproducibility Packet — what I built S11 (`deliverables/reproducibility_packet/`)

- `README.md` — cold-reader walkthrough. G-Node DOI `10.12751/g-node.d76994` (CC BY-SA 4.0) download → Py3.11 venv + `requirements.txt` → **11-step pipeline with exact CLI for every script** → expected-results table → why-clean-negative-matters → licensing/citation/scope. NO local paths, NO Collaboration Station framing, NO session history. Dataset dir is `<DATA_NIX>` placeholder; "run from repository root."
- `requirements.txt` (packet-local pins, mirror of root), `.gitignore` (packet-local), `LICENSE` (**MIT** for code — picked over Apache-2.0 per Claim Sheet "lean: MIT or Apache-2.0"), `verification_dashboard.html` (self-contained Slot-8 headline EEGNet dashboard as the reader's FIRST way in).
- **Design call I made (flagged to Codex):** did NOT duplicate `scripts/`/`utils/` into the packet — README references repo-root code by relative path, repo-as-reproduction-unit. Reason: copy-pasting forks the code, violates no-copy-paste Standard. If Codex wants a self-contained subtree instead, settle before close.
- **Pipeline ordering gotcha baked into the README:** `audit_trial_counts.py` produces `montage_intersection.json` (NOT `build_trial_metadata.py`), and `build_features --montage` consumes `montage_intersection.json` while `audit_trial_counts --montage` consumes `scalp_montage.json` — different files. Audit step MUST run before feature build.

## Division of labor (ratified)

- **Me (Claude):** data ✓ + features ✓ + LOSO ✓ + decoding ladder rungs 1–4 ✓ + mechanism co-owned (fed decoder preds ✓). **Default writer for all 4 narrative docs** — Claim Sheet ✓, Accessible Claim Sheet ✓, Technical Report (draft ✓, all P-items closed), Accessible Piece ✓ (approved). Built the Reproducibility Packet S11 (co-owned).
- **Codex:** controls/stats/harness ✓ + behavioral ablation ✓ + mechanism leads ✓ + Part B confirmatory gate ✓ (failed) + residual probe ✓ + dashboard ✓ + Technical Report [P1] figures ✓ (S12). Reviewer/approver for my docs.
- **Co-owned remaining:** Reproducibility Packet review/approval; clean-room end-to-end validation.

## Process reminders specific to me

- **Progress reports:** written 4 (Phase 0 Close, Phase 1 Close, Session 8 cadence, Amendment 1). Next **cadence** at my Session 16. Plus one at each future phase transition / approved amendment (whoever closes it writes it). **A Phase-3-close is a report trigger.**
- **Cross-review done S11:** read Codex HumanReport12 (his S12: approved Accessible Piece w/ one Part-A precision edit I agree with; confirmed [P3]; closed [P1] figures; concluded Accessible Piece Review chat). Agreed, no correction. Corrections propagate forward.
- **Amendment status:** Amendment 1 RATIFIED + on BOTH sheets + Codex final-approved. Next amendment (if any) = append-only protocol. I did NOT touch the Claim/Accessible Claim Sheets S11 (nothing changed direction).
- **GIT PROTOCOL (Randy, S8):** Codex still can't push (`.git/index.lock` permission error — confirmed not stale in his S12 report; GitHub also unreachable from his sandbox). I push his COMPLETED working-tree files alongside mine. Message format **"Claude Session N; Codex Session M"** — ONLY when Codex's session is COMPLETE; never bundle an unfinished one. **This session's push = "Claude Session 11; Codex Session 12"** (his S12 complete, `.codex-session.lock` absent at my start).
- **Session lock:** `.claude-session.lock` (create at start, delete at end). Codex uses `.codex-session.lock` — PER-AGENT. Stale lock from a crashed session is safe to clear. Scheduled task `dandelion-engineering-N` drives my sessions via `AgentPrompt.md`.
- **LaTeX IS installed on my machine** (MiKTeX: pdflatex/bibtex). Report builds clean here. **Codex's sandbox MiKTeX is broken (missing formats.ini)** — if he reports a build failure it's his env, not the source; I verify builds on my side. Build artifacts gitignored.
- **torch is NOT installed and should NOT be** (EEGNet is pure NumPy). pyriemann also not installed. Packet `requirements.txt` is framework-free by design.
- **Outputs are gitignored** (`/outputs/`, rebuildable). `deliverables/` is TRACKED (incl. the new `reproducibility_packet/` — verified `git check-ignore` returns nothing for its files; the shipped `verification_dashboard.html` is tracked, packet `.gitignore` only ignores `verification_dashboard_*.html` with a suffix). **Bash tool quirk: use forward-slash paths.** `cd` into a subdir persists in the Bash shell — use absolute paths or `cd` back to root when checking git state.
- **Python invocation:** always `.\venv\Scripts\python.exe` / `.\venv\Scripts\pip.exe` (never bare). On PowerShell tool, `& $py script.py ...`.
