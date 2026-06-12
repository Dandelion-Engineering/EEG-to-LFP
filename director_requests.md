# Director Requests — EEG to LFP

This is the single, persistent log of work that only the director (Randy) can do. Agents **append** new entries; entries are never deleted or rewritten. When Randy satisfies a request, he appends a brief reply line under it. The original entry always stays as a record. Agents may also append a note marking a request no longer needed.

---

## Request 1 — Claim Sheet ready for director review

**Date opened:** 2026-06-11 (Claude Session 3)
**Logged by:** Claude
**Status:** OPEN (non-blocking)

**What is needed:** Randy's review of the project's Phase 1 contract — both documents:
- `Claim Sheet.md` (technical contract, agent-approved rev. 2)
- `Accessible Claim Sheet.md` (plain-language companion, written for you — start here)

**Why it is needed:** This is the close of Phase 1. The framework treats your review of the Claim Sheet as the first invocation of the amendment protocol. If you approve with no changes, nothing shifts and this request closes silently. If you propose amendments, we run the standard amendment protocol and archive any work that becomes inconsistent.

**What is blocked by it:** Nothing hard. Per the framework, Phase 2 proceeds regardless of when your review lands — the agents do not sit idle waiting for it. We are starting Phase 2 (pinned dependency install + NIX data reader + the trial-count audit) immediately. Your review, whenever it arrives, is handled as an amendment cycle on top of in-progress work.

**Suggested way to review:** Read `Accessible Claim Sheet.md` end to end — it carries the same commitments as the technical sheet in plain language. If you want the technical detail on any slot, the matching section of `Claim Sheet.md` has it. The most important things to sanity-check as the director: the success bar (Slot 11), the two-halves structure of the claim (Slot 3), and the verification dashboard we've committed to building for you (Slot 8).

*(Randy: append your reply below this line when you've reviewed.)*

**Randy (via `Some Updates` chat, 2026-06-11):** "Let's consider the claim sheet approved. I trust you enough to know good work is happening either way."

**Claude (Session 8, 2026-06-12):** Closing this request as **RESOLVED** — Claim Sheet approved by the director with no amendments. The contract stands as agent-approved rev. 2. (Note: a re-pointing amendment is now *proposed* by the agents off the back of the completed decoding ladder — that runs through the standard amendment protocol and is unrelated to this approval.)

---

## Request 2 — Free disk/memory on the laptop so the EEGNet rung can run

**Date opened:** 2026-06-11 (Claude Session 7)
**Logged by:** Claude
**Status:** OPEN (blocks one analysis lane; rest of project proceeds)

**What is needed:** Free space on the C: drive (it is at ~3.1 GB free, effectively full) and/or relieve system memory pressure. With the disk nearly full, Windows cannot grow the page file, so Python/NumPy fails to allocate even small (~75 MiB) intermediate arrays during model training.

**Why it is needed:** The rung-4 EEGNet decoder (`scripts/run_eegnet_decoder.py`) trains a small convolutional net in pure NumPy. The implementation is complete and **gradient-checked** (max relative error 7e-6), and inference/training are already chunked to 32-row minibatches, but the run still dies mid-training with `numpy ... _ArrayMemoryError: Unable to allocate 75.0 MiB` / scipy `_flapack` DLL load failures — both symptoms of the page file being unable to grow on a full disk.

**What is blocked by it:** Only the EEGNet LOSO run (the final pre-registered model-class rung). Nothing else — rungs 1–3 are done, the mechanism scaffold and MTL band-power probe run fine, and the negative-decoding verdict is already strong through rung 3. EEGNet is the last lever before any amendment discussion.

**Fallback in the meantime:** The rung is left ready to execute. The moment memory/disk is freed, a single command produces the result:
`.\venv\Scripts\python.exe scripts\run_eegnet_decoder.py --data-dir "D:\Simultaneous EEG_LFP\data_nix" --bundle outputs\features\feature_bundle.npz --out-dir outputs\decoding --channel-set all`
After that, Codex's `run_control_models.py` + `summarize_subject_statistics.py` give the +0.075 test, and `run_mtl_bandpower_probe.py --signal-predictions outputs\decoding\predictions_eegnet_raw_all.csv` gives the EEGNet↔MTL coupling. No agent work is idle waiting on this.

*(Randy: append your reply below this line once memory/disk is freed.)*

**Randy (via `Some Updates` chat, 2026-06-11):** "I have cleared a substantial amount of disk space so that you could continue your work. If you had anything you wanted to try but were blocked because of disk space, you could run it now."

**Claude (Session 8, 2026-06-12):** Closing this request as **RESOLVED**. C: now shows ~430 GB free (was ~3.1 GB). The EEGNet rung ran to completion this session (mean LOSO balanced accuracy 0.616; headline success criteria NOT met — improvement +0.023, 5/9 subjects, S04-driven, not robust). EEGNet↔MTL coupling came back positive (theta−alpha corr +0.068, 7/9, p2=0.0508) where the linear/tangent decoders were null. Decoding ladder is now exhausted; amendment proposal posted in the `Riemannian Ladder Verdict` chat. Thank you for clearing the space.
