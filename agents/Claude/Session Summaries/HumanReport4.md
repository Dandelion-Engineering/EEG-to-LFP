# Human Report 4 — Claude

**Date/Time:** 2026-06-11 10:15 PDT
**Agent:** Claude
**Session:** 4
**Phase:** Phase 2 — Execution (the data layer now exists; first decoder not yet built)

---

## In one paragraph

This was the session where the project stopped being documents and started being a working pipeline. I installed the dependencies, wrote and **validated** the code that reads the brain-recording files, built a single table describing all 1,827 trials in the dataset, and ran the pre-registered "count the trials before you model" check that the Claim Sheet requires. The headline news: the working-memory-load decoding plan is still on solid ground — every one of the nine subjects has plenty of trials in both classes — but I found one genuine surprise that changes a technical detail of the plan, and I've flagged it to Codex for us to settle before any model is trained.

## A little background (so the rest makes sense)

The dataset is nine patients who, while they had electrodes both **on the scalp** (cheap, what we ultimately want to use) and **deep inside the brain** (the expensive "ground truth" we get to check against), played a memory game: they were shown a set of letters, held them in mind for a few seconds, then judged whether a probe letter had been in the set. Crucially, the number of letters varied — **4, 6, or 8** — and that number is the "working-memory load." Our first concrete claim is that scalp EEG alone can tell *high load apart from low load* during the few-second "holding it in mind" window (the **maintenance period**), and do so on a *new person it was never trained on*.

The files are stored in a scientific format called **NIX** (a standard layout built on top of the common HDF5 file format — think of it as a labeled filing cabinet for experiments). Before you can analyze anything, you need code that opens that cabinet and reliably pulls out the right drawers. That code is what I built and checked this session. ([NIX format reference](https://nixio.readthedocs.io))

## What I accomplished

1. **Installed and pinned the toolkit.** A clean, reproducible set of Python libraries (NumPy, SciPy, h5py, nixio, pandas, scikit-learn, matplotlib, pyarrow), every one under a license that permits commercial use — a hard requirement for Dandelion. Versions are frozen in `requirements.txt` so anyone, six months from now, installs exactly what we ran.

2. **Wrote the file reader** (`utils/nix_io.py`). It opens a session file and hands back the scalp recordings aligned trial-by-trial, plus a clean table of what happened on each trial (how many letters, whether they answered correctly, how fast, and the precise timing of each task event). The deep-brain electrode anatomy (needed later for the "is this really coming from the memory structures?" check) is exposed through a separate function so we don't load it until we need it — important on a laptop with limited memory.

3. **Validated the reader as a hard gate** (`scripts/validate_nix_reader.py`). This is the Dandelion "stop-or-go" discipline: before trusting a reader, prove it agrees with the dataset's own documentation *and* with an independent re-read of the same data. **All 20 checks passed.** If any had failed, the rule is to stop and diagnose rather than push forward on a shaky foundation.

4. **Discovered the task timing is beautifully clean.** Every trial, for every subject and every load level, has identical event timing: the maintenance period is always exactly the window from 3 seconds before the probe to the probe itself. Only the *response time* changes with load. Why this matters: it means the time window we analyze contains **no accidental "tell"** about how many letters there were. A skeptic's worry — "maybe you're just detecting that harder trials take longer" — is structurally ruled out for this window. That's a gift for the credibility of the eventual result.

5. **Built the master trial table** (`build_trial_metadata.py`) — one row per trial across all 37 sessions, 1,827 trials total. This is the shared contract between my work and Codex's: his statistical-controls code reads this table so it can enforce the rules (for instance, that the "could you guess load from behavior alone?" control is *forbidden* from peeking at the actual letter count).

6. **Ran the pre-model trial-count audit** (`audit_trial_counts.py`) — the check the Claim Sheet demands *before* any model runs, so our success target is judged against the real data, not adjusted after seeing results.

## What the audit found

**The good news — the success target holds.** We had pre-committed to a target of "beat the best non-brain control by at least 0.075 in balanced accuracy." Codex listed several red flags that would force us to renegotiate that target (too few trials, severe imbalance, too many discarded). **None of them fired.** The thinnest case is Subject 9 with 27 low-load and 61 high-load trials — comfortably enough. Discarded-trial rates run 3–14%, all under the 20% line. So the target stands on the trial-count side.

**The surprise — the scalp electrode layouts are not the same across people.** I had assumed all nine subjects wore the standard full cap. They didn't. Three subjects have the full 19–20 electrodes; the rest have reduced sets, four of them as few as **8**. Because our headline test trains on some people and tests on a *new* person, the model can only use electrodes that **every** subject has in common. That common set is just **8 electrodes — 6 over the brain plus 2 ear references**: frontal (F3/F4), central (C3/C4), and occipital (O1/O2).

This is a real constraint, and we didn't know it when we set the target. My read is that it *narrows but does not break* the plan: our target is about *beating controls*, not hitting some high absolute accuracy, and the statistical methods we planned (covariance-based features, Riemannian geometry) work fine on a handful of channels. So I've argued to Codex that **+0.075 should still stand**, with the headline test simply restricted to the 8 common electrodes, and the richer-cap subjects' extra electrodes used only for side diagnostics. But this is exactly the kind of decision the Claim Sheet says we lock down *before* modeling — so I've put it to Codex and will not build the decoder until we agree.

## Decisions I made

- **Validated against the dataset's own reference before trusting the reader** (Standards: scientific work is gated, not assumed).
- **Kept the maintenance window fixed at [−3, 0] seconds for all trials**, justified by the timing being identical across loads — and exposed the per-trial event times anyway so Codex's code can *assert* that invariant rather than take my word.
- **Mapped the dataset's single per-trial "artifact" flag to the rejection columns** Codex asked for, and told him plainly there is no finer scalp-vs-deep artifact flag in the data, so he doesn't design around one that doesn't exist.
- **Left the derived tables out of the git repository** (they rebuild from the scripts + the dataset) but they live locally for Codex to use immediately.

## Challenges and how I handled them

- **A file-format quirk nearly blocked everything.** The reader library crashed on some files because a few text fields (a German hospital name) aren't stored in the encoding the library expects. Rather than let one bad text field sink an entire session's read, I isolated the failure so it's ignored only for the fields we never use; all the numbers we actually need read perfectly.
- **Codex's Session 4 work was sitting uncommitted** in the workspace (his push didn't land — the same hiccup noted last session). I picked his files up in my commit so none of his work is lost, exactly as I did in Session 3.

## Files created or updated

Created (committed):
- `utils/__init__.py`, `utils/nix_io.py`, `utils/epoching.py` — the data layer
- `scripts/validate_nix_reader.py`, `scripts/build_trial_metadata.py`, `scripts/audit_trial_counts.py`
- `requirements.txt` — pinned, commercial-OK dependencies

Created (local, gitignored as rebuildable — `outputs/`):
- `trial_metadata.{csv,parquet}`, `session_summary.csv`, `scalp_montage.json`
- `trial_count_audit.{md,csv}`, `trial_count_by_setsize.csv`, `montage_intersection.json`

Updated:
- `agents/Claude/references.md` — added the NIX/nixio tooling entry
- `.gitignore` — added `/scratch/`
- `chats/Claude-Codex/Phase 2 Controls Interface/...Active.md` — my reply to Codex (field mapping, audit results, the montage question)
- This report, plus my README and continuity summary

## Next steps

1. **Codex to weigh in on the montage decision** (keep +0.075 on the 8-channel common montage — my recommendation). The decoder waits on that agreement.
2. Once agreed: **feature extraction** on the common montage — filter-bank band power + covariance over the maintenance window — followed by the LOSO logistic/LDA baseline (the first rung of the model ladder).
3. Codex can now build the controls harness against the real `trial_metadata` table.
4. The mechanism-validation layer (is the scalp signal really tied to deep-brain memory activity?) can begin its coverage audit using `read_ieeg_electrode_info`.

**Open blocker for the director:** none new. Randy's Claim Sheet review remains open in `director_requests.md` but is non-blocking.
