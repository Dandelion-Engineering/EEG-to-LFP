# Claude Session 6 Report

**Current Date and Time:** 2026-06-11 13:19 PDT

## Summary

This session had two jobs in my lane: climb the model ladder for the working-memory load decoder (rungs 2 and 3 of the pre-registered sequence), and run the medial-temporal-lobe (MTL) coverage audit that gates the mechanism half of the project. Both are done. The headline scientific outcome is an honest negative result on the decoding side and a clean pass on the mechanism gate.

### The short version, in plain terms

We are trying to decode, from *scalp* EEG alone, whether a person was holding a high vs. low memory load — and to do it in a way that transfers to people the model has never seen (leave-one-subject-out). Last session, the simplest model reached 56% balanced accuracy (50% is chance). The catch Codex found: a "control" model that ignores the brain entirely and only looks at *behavior* (how fast the person responded, whether they got the previous trial right, etc.) scored **59%**. So the brain-signal model was actually *behind* a model that doesn't use the brain at all. The pre-registered bar is that the brain model must beat the strongest such control by at least 7.5 percentage points.

My job this session was to ask: does a *smarter* model close that gap? I climbed to the most powerful classical approach for this kind of data — "Riemannian geometry," which treats each trial's pattern of co-activity across electrodes as a point in a curved space and measures distances there. It is the method that wins most EEG decoding competitions. **It did not help.** Every variant landed between 53% and 56% — tied with or slightly below the simple model, and all still behind the 59% behavioral control.

What this means: the ceiling here is not the cleverness of the model. It is the input — only 8 scalp electrodes are shared across all 9 patients, and the brain patterns are so person-specific that adding model power mostly learns *who* the person is, not *how loaded* their memory is. That is a real, useful finding, and it points the project toward its second half.

The second half is the *mechanism* question: is the scalp signal we do see actually coupled to directly-recorded deep-brain (MTL) activity? That only works for patients whose electrodes actually reached the MTL. I audited all 9 patients: **every single one has good MTL coverage** (all have hippocampus electrodes; 6 to 21 MTL contacts each). So the mechanism analysis is fully unblocked, even though the pure-decoding scoreboard is stuck.

## Educational note: what "Riemannian" buys you (and why it didn't here)

A short, link-backed explainer, since this was the session's main technical lever.

- **Covariance as a feature.** For each trial we summarize the EEG not by raw voltages but by a *covariance matrix* — a small table of how each electrode's signal co-varies with each other electrode's, per frequency band. This captures the spatial *pattern* of activity, which is more robust than raw power. ([Barachant et al., 2012](https://hal.science/hal-00681328v1/document) is the founding reference.)
- **Why "geometry."** Covariance matrices live on a curved surface, not a flat one, so ordinary straight-line averaging and distance are slightly wrong. Riemannian methods do the averaging and distance-measuring *on the curved surface*, which usually extracts more signal. The standard recipe is to find the "center of mass" of the training trials on that surface and measure every trial relative to it.
- **The honest result.** Doing this properly (rung 2) scored 0.558 — statistically the same as the flat baseline's 0.560. A purely geometric nearest-center classifier (rung 3) scored 0.533–0.545. None beat the 0.593 behavioral control. When the gain from the "right" method is zero, the limit is the data, not the math.
- **One real fix worth noting.** The geometric nearest-center method first *collapsed* — it labeled 6 of 9 held-out patients as all-one-class — because each person's overall brain activity sits in a different place on the surface, swamping the load difference. The standard remedy ([Zanini et al., 2018](https://pubmed.ncbi.nlm.nih.gov/28841546/)) is to re-center each person on their own average first; that un-collapsed it (no longer all-one-class), but still didn't lift the average. That is itself informative: the problem isn't that people are *offset* from each other, it's that the load signal is genuinely faint at this montage.

## What was accomplished

1. **Built the Riemannian toolkit (`utils/riemann.py`).** Hand-rolled, dependency-free SPD-matrix geometry: geometric (Fréchet) mean, tangent-space projection, affine-invariant distance, and an SPD regularizer. I chose to hand-roll rather than add the `pyriemann` library because the feature bundle already ships the covariance matrices and the project's efficiency standard favors the smallest sufficient solution; the module is fully validated (mean residual ~1e-9, affine-invariance to ~1e-14).
2. **Built the rung-2/3 decoder (`scripts/run_riemann_decoder.py`).** Rung 2 = filter-bank tangent space + logistic; rung 3 = minimum-distance-to-Riemannian-mean; optional unsupervised per-subject recentering. Same leave-one-subject-out folds, same "held-out subject touched once" discipline, and — deliberately — the same output file format as the rung-1 decoder, so Codex's control/statistics/dashboard scripts consume these rungs with no changes.
3. **Evaluated rung 2 against the bar** using Codex's existing scripts: improvement over strongest control = **−0.036** (3/9 subjects positive, success = no), mirroring rung 1's −0.033.
4. **Ran the MTL coverage audit (`scripts/audit_mtl_coverage.py`).** Reads each patient's depth-electrode anatomy and counts contacts in hippocampus / amygdala / parahippocampal cortex. Result: **9/9 patients adequately covered → mechanism gate PASS.**
5. **Opened a coordination chat with Codex** (`chats/Claude-Codex/Riemannian Ladder Verdict`) proposing how we proceed given the plateau.

## Challenges and how they were overcome

- **The geometric mean would not converge on real data** (its error stayed pinned at ~4.7 across all iterations). Two real bugs underneath: (1) my matrix-exponential routine was accidentally sharing an eigenvalue-flooring helper that clipped the *negative* eigenvalues a tangent vector legitimately has, which froze the iteration — fixed with a dedicated no-clip exponential; (2) the covariance matrices are stored as 32-bit floats and the wide range of EEG band power costs some of them their smallest eigenvalue in that storage, making them numerically singular — fixed by adding a tiny trace-proportional ridge before any geometry. After both fixes the mean converges to ~1e-9 in a fraction of a second per band. These are the kind of silent-failure traps the project's software standards exist to catch; I validated convergence explicitly rather than trusting it.
- **Rung-3 collapse** (described above), fixed with the standard recentering step, with the result documented honestly rather than presented as a win.

## Important decisions

- **Hand-roll the Riemannian math** instead of adding `pyriemann` (efficiency standard; `pyriemann` is BSD/commercial-OK, so this was a size choice, not a licensing one).
- **Treat recentering as transductive but label-free.** It uses the held-out subject's own *covariances* (inputs) to align them, but never their *labels*. This respects the held-out-once rule; I documented the distinction in the code and references so it can be audited.
- **Do not propose a Claim Sheet amendment unilaterally.** The plateau has real implications for whether the headline decoding claim is reachable, but EEGNet (rung 4) is still un-run and the call belongs in discussion with Codex. I flagged it as "possible amendment territory" in the chat rather than acting on it.

## What was unexpected

- The complete *flatness* of the model-ladder climb. I expected at least a small lift from proper Riemannian referencing over rung-1's identity-referenced covariances; there was none. Combined with the "subject-identity is perfectly decodable from these features" diagnostic Codex reported, this paints a consistent picture: extra model capacity buys subject identity, not transferable load signal.
- The MTL coverage being *universal* (9/9, every patient with hippocampal contacts). I expected the gate to pass but with a few marginal subjects; instead it passed decisively, which makes the mechanism half the project's strongest remaining lever.

## Files created or updated

Created:
- `utils/riemann.py` — affine-invariant SPD geometry (mean, tangent space, distance, regularizer).
- `scripts/run_riemann_decoder.py` — rung-2 (tangent) and rung-3 (MDM) LOSO decoder, optional recentering.
- `scripts/audit_mtl_coverage.py` — per-subject MTL electrode coverage audit and mechanism gate.
- `chats/Claude-Codex/Riemannian Ladder Verdict/Riemannian Ladder Verdict - Active.md` — coordination chat.
- `agents/Claude/Session Summaries/HumanReport6.md` — this report.

Updated:
- `agents/Claude/references.md` — added Zanini et al. (2018) recentering reference; annotated Barachant with the rung-2/3 result.
- `agents/Claude/README.md`, `agents/Claude/Summary of Only Necessary Context.md` — closeout.

Generated but git-ignored (rebuildable, local for Codex):
- `outputs/decoding/{predictions,subject_scores,summary}_{tangent_cov_all,tangentrc_cov_all,mdm_cov_all,mdmrc_cov_all,tangent_cov_brain}.*`
- `outputs/controls/control_*_tangent_cov_all.csv`, `outputs/statistics/*_tangent_cov_all.*`
- `outputs/mechanism/{mtl_coverage.csv, mtl_contacts.csv, mtl_coverage_summary.json}`

## Next steps / pending actions

- **Codex:** the behavioral-control ablation he proposed (split behavioral-only into response-time / correctness / previous-trial / trial-order-session components) — to learn whether 0.593 is a confound we must beat or a separate non-neural correlate of load.
- **Me (next session):** one bounded EEGNet rung (rung 4) so the model-class negative result is complete, then begin the mechanism coupling scaffold (coverage is in: 9/9).
- **Both, before any Claim Sheet change:** reconvene in the new chat once EEGNet and the ablation are in. If EEGNet also fails to beat behavioral-only, that is the moment to discuss re-centering the headline claim on the mechanism result rather than the decoding margin.
- No progress report this session (Session 6; cadence report due at Session 8; no phase transition or approved amendment triggered).
