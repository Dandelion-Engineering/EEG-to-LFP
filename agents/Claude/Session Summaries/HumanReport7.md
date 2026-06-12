# Claude — Human Report 7

**Current Date and Time:** 2026-06-11 17:07 PDT

## Summary

This session built the **fourth and final rung** of our pre-registered decoding ladder — **EEGNet**, a compact convolutional neural network that learns directly from the raw EEG waveform rather than from hand-built features. I wrote it, proved it mathematically correct, and wired it into the exact same evaluation harness as the earlier rungs. I could **not run it**, because the laptop is currently out of usable memory and disk space. The rung is left ready to execute the instant that's fixed.

A quick reminder of where we are, in plain terms: we are testing whether cheap scalp EEG carries a usable, person-to-person-transferable signature of working-memory "load" (how many items someone is holding in mind), checked against gold-standard electrodes recorded inside the brain. We climb a "ladder" of progressively more powerful models. Rungs 1–3 (linear models, covariance models, and curved-geometry "Riemannian" models) all plateaued and **none beat the strongest fair comparison baseline**. EEGNet is the last model type on the ladder. If it also fails, we'll have honestly exhausted the model side of the question and the project's weight shifts to the "mechanism" half (does the scalp signature actually track deep-brain activity).

### What was accomplished

1. **Built EEGNet from scratch in pure NumPy** (`utils/eegnet.py`). Normally you'd reach for a deep-learning library like PyTorch, but that won't fit — the C: drive has under 4 GB free and PyTorch needs more than that. So, exactly as we did earlier for the Riemannian math (`utils/riemann.py`), I hand-wrote the whole network — the convolution layers, the normalization, the training optimizer — with no new dependencies. It's a faithful version of the standard EEGNet architecture (Lawhern et al., 2018), just small and self-contained.

2. **Proved the implementation is correct.** A neural network is only trustworthy if its "learning signal" (the gradient) is computed correctly. I verified every gradient against a slow-but-exact numerical reference (a "finite-difference gradient check"). It passes to a max relative error of 0.0007% — essentially exact. This matters: a negative result is only worth reporting if the tool that produced it is sound. This is the same discipline we used to validate the Riemannian rung.

   - One honest wrinkle worth recording: my first gradient check *appeared* to fail on the very first normalization layer. On inspection it was not a bug — it was a known numerical artifact of stacking three normalization layers, which makes the simple numerical reference unreliable for the earliest layer specifically. I re-did the check in a way that isolates that layer cleanly, and everything passes. I mention it because "the first check failed" is exactly the kind of thing that should be in the record, not quietly smoothed over.

3. **Wrote the decoder driver** (`scripts/run_eegnet_decoder.py`) to the *identical* evaluation contract as the earlier rungs: same trials, same "leave-one-subject-out" protocol (train on 8 people, test on the 9th, never peeking), same output files. This means Codex's existing scoring and statistics scripts will read EEGNet's results with no changes — the rung slots straight into the machinery we already built.

4. **Cross-reviewed Codex's latest work** (his Session 8). He built the first version of the "mechanism" analysis — tools to read the in-brain electrodes and measure deep-brain activity for the same trials. His finding: there is a real-looking deep-brain "load" signature (a theta-vs-alpha brainwave difference), but our current scalp decoder's output is **not** visibly tracking it yet. I reviewed it, agreed with his careful "promising but not proven" framing, and — importantly — **did not rebuild it**. My planned mechanism work was the same scaffold he'd just written, so the right move was to not duplicate it and instead plan to feed EEGNet's results into his existing tool once it runs.

### The challenge I hit (and did not overcome this session)

**The laptop is out of resources.** The C: drive is at ~3.1 GB free (effectively full). When a disk is that full, Windows can't expand its "page file" (the overflow space it uses when RAM is tight), so even modest memory requests fail. Concretely, the EEGNet training run died with `Unable to allocate 75 MiB` — a tiny amount that should never fail on a 16 GB machine, but does when the system has no headroom. I also briefly saw scipy fail to load for the same underlying reason.

I did the engineering I could on my side: I made the network process data in small 32-trial chunks for both training and prediction, so it never needs a large block of memory at once. That wasn't enough — the machine simply has no room right now. This is an **environment problem, not a code problem**, and it happens to be the exact thing Randy is about to work on (freeing up the laptop). So I've logged it as a formal blocker and stopped, rather than burning the session fighting the machine.

### Important decisions I made

- **Hand-rolled NumPy over installing PyTorch.** Forced by the disk constraint, but also the right call under our efficiency standard — the network is tiny (~2,000 parameters) and doesn't need a heavyweight framework. Zero new dependencies.
- **Gradient-check as a stop-or-go gate.** I treat the implementation as untrustworthy until the gradients are verified. The driver refuses to train until the check passes.
- **Stopped cleanly instead of forcing the run.** When the machine couldn't sustain training, I documented the blocker and handed off, rather than producing an unreliable half-run or destabilizing an already-full laptop.
- **Did not duplicate Codex's mechanism scaffold.** Cross-review surfaced that we'd both aimed at the same next step; I deferred to his existing version and re-scoped my mechanism contribution to "run his probe on EEGNet's output once it exists."

### What was found that was unexpected

- The laptop's free disk has dropped to ~3 GB (the project's environment notes assumed ~30 GB). That's now a hard constraint on what can run locally, and it's worth Randy knowing it's not just an EEGNet issue — anything memory-hungry will hit it until the disk is cleared.
- Codex independently arrived at the same "start the mechanism scaffold" step I had planned, in a parallel session. No harm done (we caught it in cross-review), but it's a small sign we should keep the active chat current about who's taking which next step.

### What is working / not working

- **Working:** rungs 1–3 decoding results; the feature pipeline; the mechanism scaffold and MTL band-power probe; the EEGNet implementation itself (verified correct).
- **Not working:** running EEGNet (and, intermittently, anything using scipy) — blocked by the machine being out of memory/disk. Logged as `director_requests.md` Request 2.

### Files created or updated

- **Created** `utils/eegnet.py` — dependency-free NumPy EEGNet (conv/BatchNorm/ELU/pooling/dropout/Adam, class-weighted loss) with a built-in finite-difference gradient check.
- **Created** `scripts/run_eegnet_decoder.py` — rung-4 LOSO decoder; loads raw maintenance-window epochs aligned to the feature bundle, trains per fold with inner-subject early stopping, writes the standard prediction/score/summary contract. Includes a NumPy `balanced_accuracy_score` so it needs no scipy/sklearn.
- **Updated** `chats/Claude-Codex/Riemannian Ladder Verdict/Riemannian Ladder Verdict - Active.md` — replied to Codex's ablation + Session 8 mechanism update; reported EEGNet built/verified/blocked; kept the chat open pending the EEGNet numbers.
- **Updated** `director_requests.md` — Request 2: free disk/memory so EEGNet can run (with the exact command to run once unblocked).
- **Updated** `agents/Claude/README.md` and `agents/Claude/Summary of Only Necessary Context.md` (workspace navigation + continuity handoff).
- *(Local-only, gitignored:* `outputs/eegnet_headline_run.log` — the failed-run log showing the memory error.*)*

### Next steps / pending actions

1. **(Blocked on the machine) Run EEGNet** once memory/disk is freed:
   `.\venv\Scripts\python.exe scripts\run_eegnet_decoder.py --data-dir "D:\Simultaneous EEG_LFP\data_nix" --bundle outputs\features\feature_bundle.npz --out-dir outputs\decoding --channel-set all`
   then the A1/A2-excluded `--channel-set brain` diagnostic.
2. **Score it:** Codex's `run_control_models.py` + `summarize_subject_statistics.py` on the `eegnet_raw_all` tag for the +0.075 test.
3. **Couple it:** `run_mtl_bandpower_probe.py --signal-predictions ...predictions_eegnet_raw_all.csv` for the EEGNet↔MTL relationship.
4. **Then, and only then,** reconvene with Codex on whether the decoding claim is unreachable from this montage and the project's center of gravity should move to the mechanism half (an amendment discussion, not a unilateral edit).
5. My first **cadence progress report** is due at my Session 8.
