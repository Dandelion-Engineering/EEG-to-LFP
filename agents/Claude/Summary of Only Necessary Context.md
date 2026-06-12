# Summary of Only Necessary Context — Claude

**Last rewritten:** 2026-06-12 (Claude Session 8)
**Current phase:** **Phase 2 — Execution (OPEN), AMENDMENT 1 RATIFIED.** Decoding ladder is **COMPLETE and EXHAUSTED** (rungs 1–4). EEGNet (rung 4) RAN this session: mean LOSO BA **0.616**, first rung to beat the 0.593 control on the mean, but **FAILS the headline bar** (improvement +0.023, 5/9, S04-driven, not robust). EEGNet↔MTL coupling positive raw (theta−alpha +0.068, 7/9, p2=0.0508) but **collapses under residualization** (Codex's probe: load 0.050, schedule 0.011, behavior 0.013). **Amendment 1 RATIFIED this session (Claude S8 proposed, Codex S9 approved w/ narrowing I adopted): claim re-pointed to two-part [A: bounded negative; B: exploratory coupling, NOT validated].**

> Re-read `/Project Details/Project Details.md` and `AgentPrompt.md` in full at session start — do not duplicate them here. This file only holds what those don't.

## #1 PRIORITY NEXT SESSION

**Amendment 1 is DONE and written into both Claim Sheets.** Do NOT re-draft it. Remaining:
1. **Codex's final read** of the exact amendment wording in `Claim Sheet.md` (substance fully agreed in the `Riemannian Ladder Verdict` chat; corrections propagate forward). When he confirms, the chat can be **concluded** with a `Summary.md` (whoever's there).
2. **Part B confirmatory coupling test** — Codex's mechanism lane; I feed decoder scores. MUST fix band/metric a priori AND require the coupling to survive residualization (not raw p2<0.05 on the already-inspected metric). Script will be Codex's.
3. **Likely open Phase 3 (deliverables)** after that — Technical Report (LaTeX), Accessible Piece, Reproducibility Packet (incl. the Slot-8 verification dashboard, not yet built). The project has a concludable result. I'm default writer for the three narrative docs.

## THE DECODING VERDICT (now COMPLETE — load-bearing)

Mean LOSO balanced acc, headline 8-ch (chance 0.50): rung1 logistic 0.560 · covariance 0.559 · rung2 tangent 0.558 · tangent+rc 0.552 · rung3 MDM 0.533 · MDM+rc 0.545 · **rung4 EEGNet 0.616**. Strongest non-signal control (behavioral-only) = **0.593**, which is almost entirely `previous_trial_correct` (a REAL predeclared task-schedule channel: incorrect→forced set-size-4 next trial; Codex's S7 ablation). **EEGNet is the ONLY rung to beat 0.593 on the mean, but fails the success bar:** improvement +0.023 (need +0.075), 5/9 subjects (need 7/9), min-leave-one-out −0.001 (need +0.04 → S04 alone carries it: S04 improvement +0.218 vs next-best +0.045), bootstrap 95% CI [−0.022,+0.081] crosses 0, sign-flip p1=0.2617. `id_diag=1.000` on every fold (subject identity perfectly decodable from covariance → extra capacity buys identity, not transferable load). **Ceiling = 8-ch common montage + cross-subject transfer, confirmed across the WHOLE pre-registered model class.** Decoding half is done.

## THE COUPLING RESULT (the live signal — Surprise of S8)

Same intracranial substrate as before (real): MTL theta−alpha load effect z=0.143, 7/9, p2=0.0156. **What changed: the EEGNet decoder score COUPLES to it where linear didn't.**
| corr(score, MTL band) | tangent (S8) | **EEGNet (S8, now)** |
|---|---|---|
| theta | −0.011 (5/9, p2=0.87) | **+0.078 (6/9, p2=0.16)** |
| alpha | −0.018 (3/9, p2=0.82) | **+0.057 (6/9, p2=0.29)** |
| theta−alpha diff | −0.015 (5/9, p2=0.81) | **+0.068 (7/9, p2=0.0508)** |
Direction consistent: better scalp decoder → tracks MTL theta more. **Not yet significant** (borderline, modest corr, exploratory). This is the first positive evidence the scalp signature relates to deep MTL activity → the basis for the amendment.

## What I did Session 8

1. Confirmed disk freed (C: ~430 GB, was ~3.1 GB) → Request 2 resolved.
2. Ran rung-4 EEGNet headline (`--channel-set all`): gradient check re-passed 4.7e-6, 8030 s, mean BA 0.616 → `predictions_eegnet_raw_all.csv`, `subject_scores_eegnet_raw_all.csv`. **NOTE: use forward-slash paths in the Bash tool** — backslashes get stripped (first launch failed: `outputsfeaturesfeature_bundle.npz`).
3. Scored it: `run_control_models.py --feature-family covariance --tag eegnet_raw_all` + `summarize_subject_statistics.py` → headline success NO (numbers above).
4. Ran `run_mtl_bandpower_probe.py --signal-predictions predictions_eegnet_raw_all.csv` → coupling positive (numbers above).
5. Ran brain-only EEGNet (`--channel-set brain`): mean BA **0.623** ≈ all-ch 0.616 → A1/A2 reference check PASSES on rung 4. `predictions_eegnet_raw_brain.csv`.
6. Verified Codex's `run_mtl_residual_coupling_probe.py` (reproduced exactly: raw 0.068 → schedule-residual 0.011).
7. Posted complete verdict + amendment proposal; Codex approved in parallel (S9) w/ narrowing; I accepted → **wrote Amendment 1 into `Claim Sheet.md` + synced `Accessible Claim Sheet.md`.**
8. Responded to Randy's `Some Updates` chat; closed Requests 1 & 2.
9. Wrote HumanReport8 + **cadence Progress Report (Session 8)** + **amendment Progress Report**. Added EEGNet citation to `references.md`.

## The approved claim (current contract — pre-amendment)

**Slot 3:** scalp EEG holds a subject-transferable, intracranially-validated MTL WM-state signature. **Primary target = WM load binary high(6/8)-vs-low(4) from MAINTENANCE [−3,0]s.** LOSO headline; within-subject diagnostic only. **Success bar:** mean LOSO balanced-acc improvement ≥+0.075 over strongest control, ≥7/9 subjects >0, no single-subject removal drops mean <+0.04. Mechanism needs ≥5 subjects adequate MTL coverage [DONE 9/9]. Ladder: logistic [✓] → covariance [✓] → Riemannian [✓] → **EEGNet [✓ RAN — fails bar]** → (foundation models optional, NOT pursued — ladder declared exhausted). **Claim Sheet APPROVED by Randy (S8, no amendments).** The re-point is a NEW proposed amendment, not yet ratified.

## Division of labor (ratified)

- **Me (Claude):** data ✓ + features ✓ + LOSO ✓ + decoding ladder (rungs 1–4 ALL DONE) + mechanism (co-owned; feed decoder preds into Codex's probe ✓). Default writer for all 4 narrative docs (Claim Sheet, Accessible Claim Sheet, Technical Report, Accessible Piece).
- **Codex:** controls/stats/harness ✓ + behavioral ablation ✓ + mechanism scaffold ✓ (leads mechanism). Reviewer/approver for my docs. Owns Part B's confirmatory coupling test (proposed).
- **Co-owned:** metrics, mechanism, Reproducibility Packet. References reconciled jointly at Phase 2.

## Process reminders specific to me

- **Progress reports:** written 4 (Phase 0 Close, Phase 1 Close, **Session 8 cadence**, **Amendment 1**). Next **cadence** at my Session 16. Plus one at each future phase transition / approved amendment (whoever closes it writes it).
- **Cross-review done S8:** re-read full `Riemannian Ladder Verdict` chat incl. Codex's S8 mechanism-scaffold turn (no new Codex human report since HumanReport8, already reviewed S7). Agreed with his "real substrate, not yet coupled" read; my EEGNet coupling result now *extends* it (coupling appears with the stronger decoder). No correction needed; corrections propagate forward, never reopen.
- **Amendment status:** **Amendment 1 RATIFIED + written** to BOTH sheets (append-dated; synced same session). The original Slots 1–15 are preserved unchanged as a recorded turn; current direction = slots AS MODIFIED BY Amendment 1 at the bottom of `Claim Sheet.md`. Director approved the sheet as-is (no changes) on 2026-06-11. Next amendment (if any) follows the same append-only protocol.
- **GIT PROTOCOL (updated by Randy S8):** Codex still can't push (his `.git/index.lock` permission error). I push his completed working-tree files alongside mine. **New message format: "Claude Session N; Codex Session M" — but ONLY when Codex's session is COMPLETE; never bundle an unfinished Codex session.** This session: no *new* completed Codex session in front of me (his last complete = S8, already committed in my S7 push), so this push is **"Claude Session 8"** alone. The combined format kicks in next time a fresh completed Codex session sits in the tree at my closeout.
- **Session lock:** `.claude-session.lock` (create at start, delete at end). Codex uses `.codex-session.lock` — PER-AGENT (Claude+Codex parallel by design). Stale lock from a crashed session is safe to clear. Scheduled task `dandelion-engineering` drives my sessions.
- **torch is NOT installed and should NOT be installed** (EEGNet is pure NumPy; disk is now free but no need). pyriemann also not installed. If either added, pin in requirements.txt (both BSD/commercial-OK).
- **Outputs are gitignored** (rebuildable). The committed code produces them; don't commit `outputs/`.
