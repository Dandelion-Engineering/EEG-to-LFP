# Claim Sheet — EEG → MTL Working-Memory State (First Rung toward "Electrical fMRI")

**Project:** Dandelion Collaboration Station — EEG to LFP
**Status:** PHASE 2 (Execution) — **AMENDMENT 1 RATIFIED 2026-06-12** (decoding ladder exhausted → claim re-pointed to a two-part bounded-negative + exploratory-coupling result; see Amendment log). Director approved the sheet as-is on 2026-06-11 (no changes; `director_requests.md` Request 1 closed). Original Phase 1 close: technical Claim Sheet approved rev. 2 (Codex, 2026-06-11), closeout artifacts complete (Claude Session 3). **The slots below 1–15 are the original contract and are preserved unchanged as a recorded turn; the current direction is the original text AS MODIFIED BY Amendment 1 at the bottom of this file.** Read the Amendment log before measuring any new work against the slots.
**Default writer:** Claude. **Reviewer/approver:** Codex.
**Drafted:** 2026-06-11 (Claude Session 2). **Rev. 2 (Codex review amendments):** 2026-06-11 (Claude Session 2).

> **Rev. 2 changelog (Codex's Phase-1 review, all accepted):** (1) behavioral-only control now explicitly excludes set size / any label-encoding variable [Slot 7]; (2) headline epoch fixed to the **maintenance period** [Slots 5, 7]; (3) concrete success thresholds set — binary high-vs-low load (4 vs 6/8), LOSO balanced accuracy ≥0.075 over strongest control, ≥7/9 subjects, no single-subject dependence below +0.04 [Slots 5, 7, 11]; (4) mechanism-layer **≥5-subject MTL-coverage rule** + Phase-2 coverage audit [Slots 9, 11, 13]; labor split ratified with mechanism co-ownership [labor section]. These are pre-approval draft revisions, not post-approval amendments — the amendment log below stays empty until the sheet is agent-approved.

> This is the technical contract for the project. It is read at the start of every session and every result is measured against it. The companion **Accessible Claim Sheet** (written after agent approval) carries the same content in plain language for the director. The two are kept in sync via the amendment protocol; drift between them is a defect.

> **North-star context.** The director's long-term goal is "electrical fMRI": reconstructing spatially- and temporally-resolved deep-brain activity from cheap scalp EEG plus AI. That is a multi-project arc. **This Station scopes and executes the smallest sufficient *first* claim that makes real, verifiable progress toward it**, validated against a dataset of simultaneous scalp EEG / iEEG / LFP / MTL single-unit recordings. The first rung is chosen with the whole staircase in mind: every piece of infrastructure it builds (NIX reader, event alignment, subject-held-out evaluation harness, feature/metric library, per-subject verification dashboard) is reused by the harder later rungs.

---

## Slot 1 — Domain and substrate

Human electrophysiology of verbal working memory. The substrate is the **Boran et al. (2020) open dataset** of *simultaneous* recordings from 9 epilepsy patients performing a modified **Sternberg verbal working-memory task** (temporally separated encoding / maintenance / recall periods):

- **Scalp EEG** (10–20 montage) — the cheap, accessible signal that is the project's input.
- **Intracranial EEG / LFP** (depth electrodes in and around the medial temporal lobe) — the deep "ground truth" not normally available.
- **Single-unit activity** — 1526 MTL neurons (spike times + waveforms).
- **MNI coordinates + anatomical labels** for all intracranial contacts; per-trial behavioral metadata (set size, match/mismatch, correct/incorrect, reaction time).

Format: NIX (HDF5, `.h5`), 37 session files in `D:\Simultaneous EEG_LFP\data_nix`. The dataset's defining property is **simultaneity**: scalp and deep signals from the same brain at the same moment, which is what turns "infer deep activity from the scalp" from speculation into a held-out-testable measurement.

## Slot 2 — Problem being addressed

Deep medial-temporal-lobe (MTL) activity is widely treated as invisible to scalp EEG: the skull is ~80× less conductive than brain tissue, deep fields are faint and geometrically ambiguous at the surface, and the EEG inverse problem is ill-posed for deep sources. But MTL activity **couples to cortex** during memory (load-dependent hippocampal–cortical theta–alpha synchronization; Boran 2019), and that coupling does reach the scalp (Fedele 2020 measured hippocampal-sEEG ↔ scalp-EEG theta phase-locking, peaking at left-parietal P3).

**The concrete question:** Does scalp EEG carry a *subject-transferable* signature of an intracranially-validated MTL working-memory state — enough that a model can read out that state from the scalp alone, on a person it has never seen, above strong controls? This is the smallest honest version of "pull more out of scalp EEG about deep activity than has traditionally been thought possible."

## Slot 3 — The transferable claim

> **Scalp EEG contains a subject-transferable signature of an intracranially-validated medial-temporal-lobe working-memory state: in a leave-one-subject-out evaluation on the simultaneous EEG/iEEG verbal working-memory dataset, scalp EEG alone predicts working-memory load above behavioral-, timing-, and label-shuffled controls, and the scalp-derived signal is mechanistically tied to the same MTL theta–alpha coupling that the intracranial data shows tracks load.**

The claim has two coupled halves: (a) a **decoding** result (scalp → load, LOSO, above controls) and (b) a **mechanism** result (the scalp signature is carried by the MTL-coupling channel the intracranial data validates, not by an artifactual or purely cortical-task shortcut). Half (a) is the headline; half (b) is what makes it a step toward *deep* readout rather than generic task decoding.

## Slot 4 — Constraints

- **Hardware:** RTX 4070 Laptop GPU, **8 GB VRAM**; 16 GB system RAM; ~30 GB free on C:, ~850 GB free on D:. Models and pipelines must fit and run here. (NeuroFlowNet, the closest prior art, trained on a 16 GB RTX 4080 — out of our envelope, which is itself a differentiator: we target consumer hardware.)
- **Data scale:** only **9 subjects**. This is the dominant statistical constraint. It forces subject-held-out evaluation as the headline, per-subject reporting, and conservative, interpretable models over large nets.
- **Licensing (CC BY-SA 4.0 dataset):** commercial use permitted with attribution + ShareAlike on adaptations. **Policy for this project:**
  - Raw data is **never** committed to the repo; the packet references the public G-Node DOI and instructs the reader to download it.
  - Derived figures and reports carry dataset attribution and a license notice.
  - Trained model weights and any released derived dataset are treated as **ShareAlike-sensitive**: if released, they ship under a CC BY-SA-compatible license with attribution; if their release would create an unacceptable license entanglement, they are documented but not redistributed (the packet still reproduces them from raw data + code).
  - Dandelion's own **code** is released permissively (packet ships its own license file, per Standards). The specific code license is set when the Reproducibility Packet is assembled (lean: MIT or Apache-2.0).
  - Every third-party dependency must permit commercial use; licenses documented in the packet README.
- **Ethics/safety:** de-identified public research data; no human-subjects action by the team. No medical/diagnostic claims — this is a measurement study, not a clinical tool.
- **No silent exclusions:** any subject/session/channel/trial dropped from any analysis is named with its reason in the Technical Report and preserved in the packet (Standards §Scientific work).

## Slot 5 — Methods or approach

**Input.** Scalp EEG only (10–20 channels), windowed within the **maintenance period** for the headline analysis (see below). Hand-crafted, interpretable features first: per-band power (theta, alpha, beta, low gamma if SNR supports), channel covariance / log-variance, and — for the mechanism layer only — phase/coupling features constructed so they never reuse a channel that also defines the target.

**Primary target and epoch.** **Working-memory load** — a task variable defined independently of any neural channel, available for all 9 subjects — decoded from the **maintenance period** (the headline epoch). The maintenance period is chosen because it isolates a *maintained* MTL working-memory state; an encoding-period model could win by reading transient sensory stimulus-load cues rather than the maintained deep state we care about. **Primary framing: binary high-vs-low load classification — set size 4 vs. set sizes 6/8** — matching the Boran-style low/high contrast and easiest for the director to audit. The maintenance window is pre-declared (consistent with the dataset paper's validation plots) inside the training subjects only. **Secondary diagnostics:** 3-class set-size classification, ordinal/regression on set size, and encoding/recall-period decoding — reported as diagnostics, never as the headline.

**Mechanism-validation layer.** Using the intracranial data (not as a predicted target, but as a check): confirm that (i) MTL theta–alpha coupling / persistent firing tracks load in this data as Boran 2019 reports, and (ii) the scalp features the decoder relies on are statistically tied to that MTL-coupling channel — i.e., the scalp signal is reading the deep-coupling trace, not an unrelated shortcut. Reported on whatever subset has adequate MTL coverage; that subset is named explicitly.

**Pre-declared extension ("mechanism-direct" variant).** If the primary clears its gate: predict an **intracranially-defined MTL coupling state** from scalp-only features (Codex's "option 2"), with strict target/predictor channel separation. This is the closer cousin of the north star and is run only after the primary succeeds.

**Pre-declared fast-follow (Candidate B).** Reconstruct the **time course of MTL theta/alpha band power** from scalp EEG, correlated against true iEEG band power on held-out subjects — "electrical fMRI in miniature," at the band the coupling literature says is recoverable. Region/electrode-group level, not raw per-contact vectors.

**Model ladder (smallest sufficient first; Standards §Efficiency):**
1. Regularized logistic / linear / elastic-net.
2. Filter-bank covariance + shrinkage LDA or ridge.
3. Riemannian covariance classifier (small-data diagnostic).
4. EEGNet-class compact CNN — only after baselines are locked.
5. Foundation-model transfer (LaBraM etc.) — optional later comparison only, with license + 8 GB fit verified first.

**Baselines / comparison points:** the controls in Slot 7 are the primary comparison. NeuroFlowNet provides external context (different task — waveform reconstruction, subject-specific) but is not a head-to-head baseline for state decoding.

## Slot 6 — Application and downstream relevance

If scalp EEG carries a transferable, mechanistically-grounded readout of a deep MTL state, that is the **first measurable rung** of "electrical fMRI": evidence that cheap, wearable-grade EEG plus AI can recover information about deep brain activity that conventional interpretation discards. Who it helps, eventually: anyone for whom fMRI is too expensive, too immobile, or inaccessible — researchers, and in the long arc, individuals monitoring cognition/memory affordably at home. The infrastructure built here (NIX loader, alignment, LOSO harness, feature/metric library, verification dashboard) is the foundation every later rung (band-power reconstruction → waveform reconstruction → population-firing readout) reuses. A clean **failure** is also valuable: it tells the larger program that this dataset cannot support a transferable first claim, redirecting the staircase early.

## Slot 7 — Materials and evaluation design

**Dataset:** Boran et al. 2020, G-Node DOI [10.12751/g-node.d76994](https://doi.gin.g-node.org/10.12751/g-node.d76994/), at `D:\Simultaneous EEG_LFP`. 9 subjects, 37 NIX sessions.

**Splits.** **Leave-one-subject-out (LOSO) is the headline.** All model selection — channels, bands, windows, thresholds, hyperparameters — happens *inside the training subjects only*; the held-out subject is touched once, for scoring. Adjacent windows from the same trial/subject never straddle the train/test boundary (autocorrelation-leakage guard). Within-subject results may be reported as a diagnostic ceiling, never as the headline.

**Controls (all pre-declared):**
- Label-shuffle (within training folds) — null for the decoding metric.
- Behavioral-only — non-signal covariates with **no scalp signal and excluding the target itself**: response time, correctness, match/mismatch, session, trial order, and timing. **It must NOT include set size or any variable that encodes set size** (otherwise it trivially predicts the load target and becomes uninterpretable). This isolates information the scalp signal carries *beyond* non-neural task covariates.
- Timing-only — epoch timing alone — guards against decoding the task's temporal scaffold.
- Subject-identity leakage check.
- Artifact sanity — eye/muscle/reference channels or obvious non-neural features must not dominate.

**Metrics.** Primary decoding metric: **LOSO balanced accuracy** on binary high-vs-low load during maintenance, anchored as **improvement over the strongest non-signal control** (not raw accuracy above chance), **reported per-subject** (the per-subject plot is part of the claim). Evidence is **subject-level**: a subject-level sign-flip / permutation interval is reported, and a window-level permutation may *not* substitute for subject-level evidence. Secondary metrics: AUC, 3-class/ordinal set-size scores, regression correlation/R². Mechanism layer: correlation/coherence between scalp-decoder-relevant features and MTL theta–alpha coupling, on the named MTL-coverage subset. The concrete success thresholds are pre-declared in Slot 11.

**Quality control.** Every excluded subject/session/channel/trial named with reason (Standards). Subjects lacking adequate MTL coverage are excluded from the *mechanism layer only*, not the headline decoding claim, and the list is explicit.

## Slot 8 — Director's verification path

A **per-subject verification dashboard** (static HTML/PNG report + a runnable script) that the director can open without reading the Technical Report or learning the math. For each of the 9 held-out subjects it shows, side by side:

1. the held-out subject id and what the model never saw,
2. the scalp EEG input (a representative window / feature summary),
3. the true working-memory load on each trial (task ground truth),
4. the model's scalp-only prediction,
5. the control predictions (shuffled / behavioral-only / timing-only) on the same trials,
6. the mechanism panel — the simultaneously-recorded MTL coupling signal for that subject, showing the deep activity the scalp readout is tied to,
7. a one-line plain-language verdict: does this subject **support**, **weaken**, or **contradict** the claim.

Plus one **summary view** over all 9 folds so the director sees the whole picture, not a cherry-picked trace. The director's test of belief: *"the model never saw this person, it read their scalp, it called their memory load better than the controls, and the deep recording confirms the signal it used is the real MTL coupling."* The dashboard lives **inside the Reproducibility Packet** (Standards), so any downloader verifies the same way the director does. Built incrementally across Phase 2, not assembled in the final session.

## Slot 9 — Architecture or build plan

Smallest sufficient version, with room to grow:

- **`utils/` shared module** (Standards §Software engineering): NIX/HDF5 reader, event/epoch alignment, feature extraction (band power, covariance, coupling), LOSO split manager, metrics, plotting. Imported by every script; no copy-paste.
- **Stage 1 — Data layer.** NIX reader → aligned epochs (scalp + trial metadata; iEEG/units loaded lazily for the mechanism layer). Validated against the provided MATLAB loader / `NIX_File_Structure.pdf` as a correctness gate (Standards §Scientific work: a validation step is stop-or-go).
- **Stage 2 — Feature + baseline decoding.** Hand-crafted features → model-ladder rung 1–2 → LOSO scores + controls.
- **Stage 3 — Mechanism layer.** First the **MTL-coverage audit** (count subjects with adequate MTL coverage; the ≥5 rule of Slot 11 gates the full claim). Then iEEG theta–alpha coupling + unit-firing checks; tie scalp-decoder features to the MTL channel.
- **Stage 4 — Verification dashboard.** Per-subject + summary report.
- **Growth room:** model-ladder rungs 3–5, the mechanism-direct extension, and Candidate B reconstruction plug into the same data/metric layer without rework.

Every script: one purpose, `argparse` with `required=True` for machine-specific paths, docstrings, stdout progress, named output files, loud failure on bad input.

## Slot 10 — Computational and physical environment

- **OS:** Windows 11 Home (Build 26200).
- **GPU:** RTX 4070 Laptop, 8 GB VRAM, CUDA-capable. **CPU:** i7-12700H. **RAM:** 16 GB. **Storage:** ~30 GB free C:, ~850 GB free D: (dataset lives on D:).
- **Python:** **always** `.\venv\Scripts\python.exe` and `.\venv\Scripts\pip.exe` — never bare `python`/`pip`. `venv` exists at project root (Python 3.11.9) but is currently **bare**; Phase 2's first task is a pinned dependency install.
- **Anticipated stack (pinned in `requirements.txt` at install, versions TBD at Phase 2):** `numpy`, `scipy`, `h5py` and/or `nixio` (NIX reader — license check, MIT-expected), `mne` (EEG processing), `scikit-learn`, `pandas`, `matplotlib`; `pyriemann` for the Riemannian rung; `torch` (CUDA build sized to 8 GB) only when the CNN rung is reached. Every dependency's license recorded in the packet.

## Slot 11 — What would count as success

Pre-declared, before any result is observed:

- **Headline (concrete bar):** in LOSO binary high-vs-low load decoding during maintenance, **mean LOSO balanced accuracy is ≥ 0.075 (absolute) above the strongest non-signal control**, **at least 7 of 9 held-out subjects** are above that control, **and** no single-subject removal drops the mean improvement below **0.04** (the "not carried by one subject" robustness rule). Evidence is reported at the subject level (sign-flip / permutation interval). *The +0.075 / 7-of-9 / 0.04 figures are the pre-declared first-pass bar; if a Phase-2 trial-count audit shows +0.075 is unattainably high for honest reasons, a replacement bar is proposed and agreed **before any model is run**, never after seeing results.*
- **Mechanism (coverage rule):** the deep-readout half of the claim requires **≥ 5 subjects with adequate MTL coverage** (determined by a Phase-2 coverage audit *before* mechanism analysis). On that subset, the scalp features the decoder relies on must be significantly tied to MTL theta–alpha coupling — i.e., the readout rides the validated deep channel, not an artifact or pure cortical-task shortcut. If fewer than 5 subjects qualify, the mechanism half cannot support the full claim regardless of how the available subset looks (see Slot 13).
- Both halves holding = the transferable claim (Slot 3) is supported. The headline alone, without the mechanism half, is reported as a **weaker** result (decoding works but its deep grounding is unconfirmed) — see Slot 13.

## Slot 12 — What would count as failure

Pre-declared:

- **Clean failure:** within-subject decoding exists but **LOSO decoding does not beat the controls** — scalp EEG does not carry a *transferable* signature of this MTL state in this dataset. Honest, publishable, and informative for the larger program (it says the first rung needs per-subject calibration or more subjects). Reported as a failure, not buried.
- **Mechanism failure (with decoding success):** LOSO decoding beats controls, but the scalp signature is **not** tied to the MTL-coupling channel (it tracks load via a cortical/task/artifact route with no deep grounding). This does not support the *deep-readout* claim; it is reported as "transferable load decoding, but not via a validated deep signature" (a partial result, Slot 13), not as the headline claim.

## Slot 13 — What would count as inconclusive / non-transfer

- **High variance across 9 subjects** — the summary metric's confidence interval spans the control band, or the result flips depending on which subjects are included. Reported as inconclusive; not spun as success.
- **Insufficient MTL coverage** — **fewer than 5 subjects** with adequate MTL coverage (per the Slot 11 coverage rule). The decoding half may still stand, but the mechanism half is reported as *too sparse / inconclusive in this dataset*, and the claim is downgraded to "load decoding with mechanism evidence too sparse" — never the full deep-readout claim, even if the available subset looks positive.
- **Decoding-without-mechanism** (Slot 12 second case) sits here as a real, named partial outcome: "not the full claim, not nothing." Recorded so a partial win is never reported as a full one.

## Slot 14 — Minimum public artifact required to conclude the project

1. **Technical Report (LaTeX):** claim, methods, materials, LOSO evaluation design, controls, per-subject results, mechanism-layer results, limitations (esp. n=9), and conclusion — including any clean failure/inconclusive outcome stated plainly.
2. **Accessible Piece:** the same project for a non-technical reader — what was done, why it matters, what was found.
3. **Reproducibility Packet:** `utils/` + stage scripts, pinned `requirements.txt`, its own `.gitignore` and license, a top-level README that walks an outside reader from downloading the public dataset through reproducing every result, and the **verification dashboard** (Slot 8) as the reader's first way in. No raw data in the repo; the public G-Node DOI is referenced. Reproducible end-to-end on a fresh environment given the dataset path.

## Slot 15 — Possible monetization paths

- **If it succeeds as scoped:** primarily a **research enabler**, not a product yet. Path opened: a validated, open first rung that de-risks the larger "electrical-fMRI" arc and makes a credible case for the next (better-resourced) project; potential to offer the analysis pipeline / LOSO-validated decoding methodology as a consulting or licensed component to EEG-research groups.
- **If pushed further / scaled in a future project:** the north-star device — affordable scalp-EEG + AI giving a coarse deep-activity picture — is the long-horizon consumer/clinical-research monetization path (affordable cognition/memory monitoring). Far future; named to keep the thread visible, not committed here.
- **Honest note:** `none identified` for *this* rung as a standalone product. Its commercial value is as a verified stepping stone, which is the correct shape for a first-rung research project.

---

## Pre-declared division of labor (to ratify in Phase 1 chat)

- **Writing:** Claude drafts Claim Sheet, Accessible Claim Sheet, Technical Report, Accessible Piece; Codex reviews/approves. Both contribute to the Reproducibility Packet; references reconciled jointly at Phase 2.
- **Build (ratified in Phase 1 chat, 2026-06-11):** Claude owns the data layer (NIX reader, alignment, LOSO harness, feature extraction) + primary load-decoding pipeline. Codex owns the controls/statistics specification and harness (label-shuffle, behavioral-only [target-excluded], timing-only, autocorrelation guard, subject-level permutation/uncertainty) + the verification dashboard's per-subject rendering. **Mechanism-validation analysis (iEEG theta–alpha coupling, unit firing, the Phase-2 MTL-coverage audit) is co-owned** — Codex leads the analysis, but it depends on Claude's NIX reader and alignment code exposing the iEEG/unit inputs, so the two are coupled. Co-owned: metrics, Reproducibility Packet.
- Amendable via the standard protocol if the work calls for it.

## Amendment log

**Director review (2026-06-11):** Randy approved the Claim Sheet as-is, with no changes ("let's consider the claim sheet approved"), via the `Claude-Codex-Human/Some Updates` chat. The first amendment cycle (director review) therefore closed with no modifications; the contract stood unchanged until Amendment 1 below. `director_requests.md` Request 1 closed.

---

### Amendment 1 — Decoding ladder exhausted: re-point from "scalp beats baseline" to "bounded negative + exploratory MTL coupling"

**Date ratified:** 2026-06-12
**Proposed by:** Claude (Session 8). **Approved by:** Codex (Session 9), with a narrowing of the Part B language that Claude adopted in full. Consensus reached in `chats/Claude-Codex/Riemannian Ladder Verdict/`.
**Nature:** This amendment **activates pre-declared outcomes** (Slots 12 and 13) and re-points the reportable claim and deliverables accordingly. It is not a goalpost move — the success bar in Slot 11 was held fixed, tested across the entire pre-registered model ladder, and not met. No executed work is invalidated; nothing is archived (the decoding runs become Part A's evidence, the coupling runs become Part B's).

**What was found (the trigger):**
- The pre-registered model ladder (Slot 5) is **complete and exhausted**. Mean LOSO balanced accuracy on the headline 8-channel common montage (chance 0.50; strongest non-signal control = behavioral-only 0.593, itself almost entirely the predeclared `previous_trial_correct` task-schedule channel): rung 1 logistic 0.560 / covariance 0.559 · rung 2 tangent 0.558 · rung 3 MDM 0.533–0.545 · **rung 4 EEGNet 0.616**.
- EEGNet is the **only** rung to exceed 0.593 on the mean, but it **fails the Slot 11 success bar**: mean improvement **+0.023** (bar ≥+0.075); **5/9** subjects above strongest control (bar ≥7/9); the positive mean rests entirely on subject S04 (+0.218; next-best +0.045), so removing S04 drops the leave-one-subject-removed mean to **−0.001** (bar ≥+0.04 — the robustness clause catches it); bootstrap 95% CI [−0.022, +0.081] crosses zero; subject sign-flip p1=0.262. The A1/A2 reference check passes (brain-only 6-ch EEGNet 0.623 ≈ all-ch 0.616), so this is not a reference artifact — it is a genuine sub-threshold result.
- **Mechanism half:** the intracranial MTL substrate is real (theta-minus-alpha load effect z=0.143, 7/9 subjects, two-sided sign-flip p2=0.0156). The EEGNet decoder score shows a **raw** positive coupling to it (corr theta-minus-alpha diff +0.068, 7/9, p2=0.0508) where the linear/Riemannian decoders showed none (≈−0.01) — but that raw coupling **does not survive residualization**: load-residual +0.050 (p2=0.133), schedule-residual +0.011 (p2=0.746), behavior-residual +0.013 (p2=0.715). At n=9 the dataset cannot disambiguate a real load-linked shared MTL state from a schedule-linked correlate.

**What changes:**

- **Slot 3 (transferable claim) is re-pointed** to a two-part result, replacing the single coupled claim:
  - **Part A — Bounded negative (decoding):** *Across a pre-registered ladder of model classes (regularized linear → filter-bank covariance → Riemannian → compact CNN/EEGNet), scalp EEG from an 8-channel common montage does not yield a subject-transferable working-memory-load decoder that beats the strongest non-signal control by ≥+0.075 under LOSO; the best model (EEGNet) reaches +0.023 and fails the robustness clause.* A rigorously characterized boundary.
  - **Part B — Exploratory mechanism lead (not validated):** *The strongest scalp decoder's output shows a suggestive raw coupling to simultaneously-recorded MTL theta-alpha dynamics (7/9 subjects, p2≈0.05), but that coupling does not survive stricter load/schedule residualization; the mechanism result is therefore exploratory/inconclusive, not a validated deep readout.* This is the most plausible next signal to test with a better-powered or differently structured dataset.

- **Slot 11 (success):** the headline success bar was **not met** and is not weakened retroactively — it stands as the (unmet) bar. The amended project's deliverable success is the *honest, complete characterization* of Part A (the negative boundary) and Part B (the exploratory lead with full residualization context), not a decoding win.

- **Slot 12 / Slot 13 (failure / inconclusive) — ACTIVATED:** the outcome is the pre-declared **Slot 12 clean failure** ("within-subject decoding may exist but LOSO decoding does not beat the controls") for the headline decoding claim, now established across the *entire* model ladder rather than a single model; and the **Slot 13 inconclusive** shape for the mechanism half ("decoding-without-validated-mechanism" + a coupling that does not survive residualization at n=9). Both were named before any result was observed; Amendment 1 records which resolved.

- **Slot 5 pre-declared extensions NOT run:** the "mechanism-direct variant" and "Candidate B (band-power reconstruction)" were each gated on the primary clearing its bar (Slot 5). The primary did not clear it, so per the original gating these extensions **do not run**. The project concludes on the bounded result rather than opening further rungs.

- **Part B confirmatory test (new, prospective):** a single pre-registered confirmatory coupling test is defined for Part B, owned by Codex (mechanism lane); Claude feeds decoder scores. To avoid laundering the exploratory p2=0.0508 (a max over a 6-metric family) into a headline, the test **fixes the band/metric a priori** and **requires a residualization/robustness criterion** (the coupling must hold after load/schedule residualization), not raw p2<0.05 on the already-inspected metric. If it does not clear that, Part B remains reported as exploratory/inconclusive.

- **Labor split:** unchanged except that Codex explicitly owns the residual/confirmatory mechanism analysis scripts (`run_mtl_residual_coupling_probe.py` and the confirmatory test); Claude remains default writer for all four narrative deliverables, now drafting them around the two-part result.

- **Phase signal:** with the ladder exhausted and the mechanism lead exploratory, the project has a concludable result. The likely next stretch is **Phase 3 (deliverables)** — Technical Report, Accessible Piece, Reproducibility Packet — possibly preceded by Codex's confirmatory coupling test. Not formally opened by this amendment.

**Accessible Claim Sheet:** synced in the same session (Claude Session 8) with a matching plain-language Amendment 1 entry.

**Director note:** this is the framework working as designed — a pre-declared clean failure plus a pre-declared inconclusive, both caught honestly by controls written before any result was seen. A clean failure is still a public artifact (Slots 6, 12). The result tells the electrical-fMRI arc where the first rung's wall is (8-channel common-montage cross-subject load decoding) and names the most plausible next signal (MTL theta-alpha coupling, tested with more power).
