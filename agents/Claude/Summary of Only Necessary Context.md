# Summary of Only Necessary Context — Claude

**Last rewritten:** 2026-06-11 (Claude Session 7)
**Current phase:** **Phase 2 — Execution (OPEN).** Decoding ladder rungs 1–3 negative (nothing beats behavioral-only control 0.593). **Rung 4 EEGNet is BUILT + GRADIENT-CHECKED but the LOSO run is BLOCKED by machine memory.** Mechanism gate 9/9 PASS; Codex built the mechanism scaffold (S8).

> Re-read `/Project Details/Project Details.md` and `AgentPrompt.md` in full at session start — do not duplicate them here. This file only holds what those don't.

## #1 PRIORITY NEXT SESSION (do this first, it's blocked on the machine)

**Run the EEGNet rung the moment the laptop has memory/disk.** It is fully written and verified; it just couldn't execute (see blocker below). Command:
```
.\venv\Scripts\python.exe scripts\run_eegnet_decoder.py --data-dir "D:\Simultaneous EEG_LFP\data_nix" --bundle outputs\features\feature_bundle.npz --out-dir outputs\decoding --channel-set all
```
Then `--channel-set brain` (A1/A2-excluded diagnostic). Then score it (Codex's `run_control_models.py --feature-family covariance` + `summarize_subject_statistics.py` on tag `eegnet_raw_all` → +0.075 test) and couple it (`run_mtl_bandpower_probe.py --signal-predictions outputs\decoding\predictions_eegnet_raw_all.csv`). THEN reconvene in the `Riemannian Ladder Verdict` chat on amendment.

## THE BLOCKER (director_requests.md Request 2)

**The C: drive is at ~3.1 GB free (effectively full).** Windows can't grow the page file, so NumPy/scipy fail to allocate even ~75 MiB mid-training. EEGNet training dies with `_ArrayMemoryError: Unable to allocate 75.0 MiB`; scipy intermittently fails `_flapack` DLL load for the same reason. This is **environment, not code** — Randy is actively working on freeing the laptop. Training already minibatches at 32 and I chunked inference to 32-row batches; the machine still can't sustain it. (Project Details' "~30 GB free" estimate is stale.)

## What I built Session 7

- **`utils/eegnet.py`** — dependency-free NumPy EEGNet (Lawhern 2018: temporal conv → depthwise spatial conv groups=F1 → separable conv → dense; F1=8, D=2, F2=16, kt=64, kt2=16, pools 4 then 8). Hand-rolled (no Torch — disk can't host it; same precedent as `riemann.py`). Includes grouped conv2d fwd/bwd via im2col, BatchNorm (train + eval), ELU, avgpool, dropout, Adam, class-weighted softmax-CE. **`gradient_check()` PASSES at max rel error 7e-6** (isolated train-mode BN check + well-conditioned eval-mode full-network check). NOTE: a naive all-train-mode full-network grad check spuriously "fails" on the FIRST BatchNorm's gamma/beta (~5e-3) — that's finite-difference ill-conditioning from stacked train-mode BNs, NOT a bug (Wt's grad through that same BN is exact at 9e-8). The two-part check in the file is the correct validation; don't "fix" the BN backward.
- **`scripts/run_eegnet_decoder.py`** — rung-4 LOSO driver. Loads RAW maintenance-window epochs ([-3,0]s → 600 samples @200Hz) from NIX, restricts to locked 8-ch montage, **aligns to the feature bundle's exact kept trials** (same artifact drops/labels/subjects → directly comparable to rungs 1–3). Per-channel z-score fit on TRAIN only. LOSO held-out-once; inner-subject grouped val split (`--n-inner-val 2`) for early stopping, then refit on all train subjects for the selected epoch count, score test once. `--channel-set {all,brain}`. **Output contract identical to `run_riemann_decoder.py`** → `predictions_eegnet_raw_all.csv` (trial_id, signal_pred, signal_score, load_binary), `subject_scores_eegnet_raw_all.csv` (subject_id, signal_ba), `summary_eegnet_raw_all.json`. Has its own NumPy `balanced_accuracy_score` so it needs NO scipy/sklearn (avoids the `_flapack` failure).

## THE DECODING VERDICT (load-bearing, unchanged from S6, now corroborated)

Mean LOSO balanced acc, headline 8-ch (chance 0.50): rung1 logistic 0.560 · covariance 0.559 · rung2 tangent **0.558** · tangent+rc 0.552 · rung3 MDM 0.533 · MDM+rc 0.545. **NONE beats behavioral-only control 0.593.** Codex's S7 ablation: the 0.593 control is almost entirely `previous_trial_correct` (0.596, 9/9) — a REAL predeclared task-schedule channel (dataset rule: incorrect response → next trial forced set-size-4; high-load given prev-correct=1 is 0.670 vs 0.015 given prev-correct=0). So 0.593 is a valid strongest non-signal control, not leakage. `id_diag=1.000` (subject identity perfectly decodable from covariance) → extra capacity buys identity, not transferable load. Ceiling = 8-ch montage + cross-subject transfer, NOT model class. **My prior: EEGNet also unlikely to clear 0.593, but we run it to complete the ladder before any amendment.**

## MECHANISM (half B) — Codex leads, co-owned; scaffold DONE (S8)

Coverage gate **9/9 PASS** (S6). Codex S8 built: `utils/mechanism.py` (shared MTL anatomy: Hipp/Amyg/PhG), `utils.nix_io.load_ieeg_epochs`, `scripts/run_mtl_bandpower_probe.py` (MTL maintenance-window theta/alpha log-power; load effects + correlation with a scalp decoder score file). Result on tangent rung: **MTL theta-minus-alpha load effect z=0.143, 7/9, p2=0.0156 (real-looking substrate)**, but corr(tangent score, MTL bands) ≈ −0.01 n.s. → scalp decoder NOT yet riding the substrate. **I did NOT rebuild this** (cross-review caught that my planned scaffold == his). My mechanism contribution is now: run his probe against EEGNet predictions once they exist.

## The approved claim (unchanged)

**Slot 3:** scalp EEG holds a subject-transferable, intracranially-validated MTL WM-state signature. **Primary target = WM load binary high(6/8)-vs-low(4) from MAINTENANCE [−3,0]s.** LOSO headline; within-subject diagnostic only. **Success bar:** mean LOSO balanced-acc improvement ≥+0.075 over strongest control, ≥7/9 subjects >0, no single-subject removal drops mean <+0.04. Mechanism needs ≥5 subjects adequate MTL coverage [DONE 9/9]. Ladder: logistic [✓] → covariance [✓] → Riemannian [✓] → **EEGNet [built+verified, RUN PENDING]** → (foundation models optional).

## Division of labor (ratified)

- **Me (Claude):** data ✓ + features ✓ + LOSO ✓ + decoding ladder (rungs 1–3 ✓, rung-4 EEGNet built/verified, run pending) + mechanism (co-owned, feed EEGNet preds into Codex's probe). Default writer for all 4 narrative docs.
- **Codex:** controls/stats/harness ✓ + behavioral ablation ✓ (S7) + mechanism scaffold ✓ (S8, leads mechanism). Reviewer/approver for my docs.
- **Co-owned:** metrics, mechanism, Reproducibility Packet. References reconciled jointly.

## Process reminders specific to me

- **Progress reports:** written 2 (Phase 0 Close, Phase 1 Close — phase triggers, not cadence). Next **cadence** report due at my **Session 8** (this was Session 7). Plus one at each future phase transition / approved amendment.
- **Cross-review done S7:** read Codex's HumanReport8 (mechanism scaffold) + his S7/S8 chat turns. Agreed with his ablation + "real substrate, not yet coupled" mechanism read. No correction needed; deferred to his scaffold rather than duplicating.
- **Amendment status:** NONE triggered. Ladder plateau is expected headroom territory per Claim Sheet. EEGNet result is the gate before any amendment conversation — discuss with Codex in the OPEN chat FIRST. Claim Sheet ↔ Accessible Claim Sheet sync only on an actual amendment.
- **Git:** Codex's pushes keep failing (`.git/index.lock` permission error on his side — confirmed again S8). I commit his working-tree files alongside mine. If `.git/index.lock` errors recur, check it's stale before removing.
- **Session lock:** `.claude-session.lock` (create at start, delete at end). Codex uses `.codex-session.lock` — locks are PER-AGENT (do not mutually exclude; Claude+Codex parallel sessions are by design). NOTE: a crashed session leaves a stale lock that blocks future Claude sessions — if you find a stale `.claude-session.lock` from a dead session, it's safe to clear. Scheduled task `dandelion-engineering-6` (mis-numbered; Randy will fix) drives my sessions.
- **One active chat OPEN:** `Riemannian Ladder Verdict` — do NOT conclude until the EEGNet numbers + EEGNet↔MTL coupling land and the next-direction/amendment decision is settled.
- **torch is NOT installed and should NOT be installed** (disk can't host it; EEGNet is pure NumPy). pyriemann also not installed. If either is ever added, pin in requirements.txt (both BSD/commercial-OK).
