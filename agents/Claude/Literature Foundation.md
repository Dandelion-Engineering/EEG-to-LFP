# Literature Foundation — Claude

**Project:** EEG → deep/MTL activity ("electrical fMRI," first rung)
**Phase:** 0 — Literature Review
**Author:** Claude
**Date:** 2026-06-11
**Status:** Complete pending cross-comparison chat with Codex (Phase 0 closes only after both Foundations exist and the agents align).

> Scope note. The director's north star is "electrical fMRI": reconstructing spatially- and temporally-resolved deep-brain activity from cheap scalp EEG plus AI. That is a multi-project arc. This Station's job is to scope the **smallest sufficient first claim** that makes real, *verifiable* progress toward it, validated against the simultaneous scalp-EEG / iEEG / MTL-unit dataset already on disk (`D:\Simultaneous EEG_LFP`). This document surveys the field so the Phase-1 Claim Sheet's method choices, baselines, metrics, and success/failure shapes are grounded in what the literature has already established — not invented in the same session the contract is written.

Every source cited here was located via live web search this session and carries a working link or DOI. Sources are migrated into `references.md` in the same workspace.

---

## 1. Domain and methods landscape

The project sits at the intersection of three established research threads. Understanding where each one is strong and where it breaks is what lets us pick a first claim that is ambitious but not fantasy.

### 1a. The EEG inverse problem (classical source localization)

Scalp EEG measures voltages at the surface produced by summed post-synaptic currents inside the head. Recovering the underlying sources from those surface voltages is the **EEG inverse problem**, and it is fundamentally *ill-posed*: infinitely many internal source configurations can produce the same scalp pattern, because the forward map (sources → scalp) is many-to-one and the head is a volume conductor that low-pass spatially blurs and attenuates deep signals. Practical solvers add constraints — minimum-norm (MNE, sLORETA, eLORETA), beamformers (LCMV), or sparse/Bayesian priors — to pick one solution out of the infinite set. Two facts from this literature are load-bearing for us:

- **Deep sources are the hard case.** Skull conductivity (~0.004 S/m) is roughly 80× lower than brain/scalp (~0.33 S/m), so the skull attenuates and smears the signal, and contributions fall off with distance. Subcortical/MTL sources are therefore faint and geometrically ambiguous at the scalp — exactly the structures we care about. (Vorwerk et al., conductivity uncertainty review; Frontiers in Neuroscience 2019.)
- **Forward model accuracy gates everything.** Leadfield matrices depend on head geometry and tissue conductivities that are uncertain and expensive to compute (cited figures: ~40 min and ~10 GB RAM per leadfield under conductivity sweeps). Errors in the forward model propagate directly into inverse estimates.

The classical view has long held that hippocampus/MTL is essentially *invisible* to scalp EEG. The newer literature (below) complicates that view rather than overturning it: deep activity may be unrecoverable as a *field* while still leaving statistical *signatures* at the scalp via its coupling to cortex.

### 1b. Deep-learning source imaging and signal-to-signal reconstruction

Two distinct DL framings appear, and conflating them is a common error:

- **Learned inverse / source imaging.** CNNs and hybrid physics-init networks learn a mapping from scalp sensors to a source grid, often trained on simulated data from a realistic head model. Recent work explicitly targets **subcortical** sources: a CNN with a realistic head-conductivity model localizes both cortical and subcortical M/EEG sources, validated against simulation, evoked potentials, and *invasive* recordings (APL Bioengineering 2024 / bioRxiv 2024.04.30.591970). Hybrid methods like **3D-PIUNet** start from a physics-informed pseudo-inverse estimate, then refine with a 3D U-Net data prior (arXiv:2411.00143). These are the spiritual ancestors of the director's "PINN" intuition.
- **Signal-to-signal reconstruction (scalp → intracranial).** Rather than estimating a source grid, this framing learns to map scalp channels directly onto intracranial channels. The closest prior art to this project is **NeuroFlowNet** (arXiv:2603.03354, 2026): a conditional normalizing flow with multi-scale architecture and self-attention that performs "the first-ever reconstruction of iEEG signals from the entire deep temporal lobe region using scalp EEG," validated on a public synchronized sEEG–iEEG dataset along three axes — temporal waveform fidelity, spectral feature reproduction, and functional-connectivity restoration. This paper is both an opportunity (it proves the framing is publishable and tractable) and a constraint (a pure waveform-reconstruction first claim may now be partly occupied; we should differentiate — e.g., MTL-unit/LFP-band targets, working-memory-state validation, or efficiency on consumer hardware).

### 1c. Representation learning for EEG (foundation models)

A fast-moving thread builds large self-supervised transformers on thousands of hours of EEG, producing transferable representations that fine-tune well on small downstream datasets — directly relevant because our dataset is small (9 subjects). Key anchors: **LaBraM** (ICLR 2024 spotlight; neural-tokenizer + masked modeling on ~2,500 h; arXiv:2405.18765), **EEGPT**, and **CBraMod** (criss-cross transformer, ICLR 2025). The relevant lesson: pretrained EEG encoders may let us extract more from 9 subjects than training from scratch would — but licenses and compute fit (8 GB VRAM) must be checked per model before adoption.

### 1d. LFP ↔ spike and signal-to-signal neural decoding

Below the iEEG level, there is a literature on inferring one neural signal from another: inferring spiking activity from LFP with deep learning (bioRxiv 2020.05.02.074104), and cross-modal spike-informed LFP modeling. These matter because the dataset uniquely contains MTL **single-unit** activity, so a first claim *could* reach below iEEG toward population firing — though that is the harder end of the difficulty gradient and likely a later rung.

---

## 2. Benchmark results (what performance ranges are typical)

There is no single canonical benchmark for "deep activity from scalp," because the sub-problems differ. Useful anchors by sub-problem:

- **Scalp→iEEG waveform reconstruction.** NeuroFlowNet (arXiv:2603.03354) is the current reference point for deep-temporal-lobe reconstruction; it reports fidelity on waveform, spectral, and connectivity axes rather than a single scalar. Specific numeric values were not in the abstract and need extraction from the full paper — **action item for Phase 1** (and a target to beat or differentiate from). Reconstruction quality in this family is typically reported as Pearson correlation / spectral error / coherence recovery per band, not classification accuracy.
- **DL subcortical source localization.** Reported as localization error (mm) and correlation against ground truth; the realistic-head CNN work validates against invasive recordings, which is the credibility bar we should hold ourselves to since we *have* invasive ground truth.
- **Joint scalp+iEEG classification (clinical).** As an *upper-bound sanity check* on how much usable information scalp EEG carries about deep events: CNNs classifying seizure/pre-seizure/non-seizure epochs from simultaneous recordings exceed ~98% accuracy, and "surface-negative" mesial-temporal seizures invisible to a human reader were still detected/lateralized by ML (Frontiers in Neurology 2021, PMC8632629). This is strong evidence that scalp EEG carries decodable deep-origin information even when expert visual reading says it does not — the central bet of this project.
- **Working-memory state decoding** (a candidate first-claim target): load/set-size and theta-coupling effects in this exact paradigm are statistically robust at the group level (see §3), but scalp-only single-trial decoding accuracies for this dataset are, as far as this search found, **unestablished** — a genuine open slot.

Takeaway for the Claim Sheet: our success metric should almost certainly be **correlation/coherence against simultaneous iEEG ground truth** (the dataset's defining advantage), with a decoding-accuracy framing as a secondary, more interpretable axis. Pre-declare per-band, per-region, and hold out subjects to test generalization.

---

## 3. Dataset and resource landscape

### The primary dataset (already on disk)

**Boran, Fedele, Steiner, Hilfiker, Stieglitz, Grunwald, Sarnthein et al. (2020),** *Dataset of human medial temporal lobe neurons, scalp and intracranial EEG during a verbal working memory task,* **Scientific Data** 7:30. DOI [10.1038/s41597-020-0364-3](https://www.nature.com/articles/s41597-020-0364-3). G-Node DOI [10.12751/g-node.d76994](https://doi.gin.g-node.org/10.12751/g-node.d76994/).

- 9 subjects (epilepsy patients), modified **Sternberg** verbal WM task with temporally separated encoding / maintenance / recall.
- Simultaneous **scalp EEG (10–20)**, **iEEG depth electrodes**, **1526 MTL single units** (waveforms + spike times), plus **MNI coordinates and anatomical labels** for all intracranial contacts, and trial metadata (set size, match/mismatch, correct/incorrect, RT).
- Format: NIX (`.h5`) per session; MATLAB loader provided. **License: CC BY-SA 4.0** (verified from the dataset's `LICENSE` file) — permits commercial use with attribution + share-alike on adapted material, which fits Dandelion's licensing standard. *ShareAlike applies to adaptations of the dataset itself; we must confirm how that interacts with derived model weights and reports — flag for Phase 1.*

This dataset is the project's entire reason for tractability: it provides **simultaneous ground truth** at three depths (scalp / iEEG / units) from the same person at the same moment, turning "infer deep activity from scalp" from speculation into a measurable, held-out-testable claim.

### Companion analysis papers from the same group (define what's already known about scalp↔deep coupling in this exact data)

- **Boran et al. (2019),** *Persistent hippocampal neural firing and hippocampal-cortical coupling predict verbal working memory load,* **Science Advances** 5(3):eaav3687. DOI [10.1126/sciadv.aav3687](https://www.science.org/doi/full/10.1126/sciadv.aav3687). Shows high WM load → increased persistent hippocampal *unit* firing **and** increased hippocampus–cortex coupling via synchronized **theta–alpha** oscillations. This is the mechanistic backbone: deep activity is coupled to cortex in a load-dependent, oscillatory way — the very channel by which it could leave a scalp signature.
- **Fedele et al. (2020),** *Functional synchronization between hippocampal sEEG, parietal ECoG and scalp EEG during a verbal working memory task,* bioRxiv [10.1101/2020.06.05.136515](https://www.biorxiv.org/content/10.1101/2020.06.05.136515v1.full). Directly measures hippocampal-sEEG ↔ **scalp-EEG** phase-locking; WM maintenance enhanced theta-band (~6–7 Hz) PLV specifically to **left parietal P3**. This is near-direct evidence that *scalp channels carry a measurable trace of deep MTL coupling in this dataset* — and even hints at which scalp channels/bands to weight.

### Other open datasets / assets (substitutes and pretraining)

- Large public EEG corpora (TUH/TUEG, etc., ~thousands of hours) underpin the foundation models; usable for pretraining/feature extraction subject to license checks.
- Pretrained EEG encoders: LaBraM (arXiv:2405.18765, public code), EEGPT, CBraMod — candidate transfer-learning backbones; **must verify each repo's license and VRAM footprint**.

### Compute envelope (from Project Details)

RTX 4070 Laptop, **8 GB VRAM**, 16 GB system RAM, ~850 GB free on D:. This is a real constraint: it favors compact models, per-band/per-channel targets, subject-wise cross-validation over giant end-to-end nets, and rules out training large foundation models from scratch (fine-tuning only). Efficiency is a Dandelion standard, not an afterthought.

---

## 4. Failure modes (what has been tried and does not work)

Often the most useful section for sharpening the claim. From the literature:

1. **Treating deep reconstruction as a pure inverse-field problem fails for MTL.** Volume conduction makes deep fields faint and non-identifiable at the scalp; naive minimum-norm-type solutions smear sources to the cortical surface. The productive reframing is *statistical signature via coupling* (decode/reconstruct deep activity using its learned relationship to cortex), not *direct field recovery*. The director's own intuition already points here.
2. **Forward-model misspecification corrupts learned inverses.** DL source imagers trained on simulated leadfields inherit conductivity/geometry errors. Any physics-informed component we build must treat the head model as uncertain, not exact (conductivity-uncertainty literature, Frontiers 2019).
3. **"Invisible to the expert eye" ≠ "absent from the signal."** Most hippocampal IEDs are not visible on routine scalp EEG (PMC8590709; Seizure 2022, S0920121122000651), and scalp-negative mesial-temporal discharges still perturb large-scale networks (Roehri et al., Epilepsia, [10.1002/epi.70061](https://onlinelibrary.wiley.com/doi/10.1002/epi.70061)). The failure mode to avoid is concluding "no scalp signal" from human-reader negativity — ML repeatedly extracts what readers miss. Conversely, the *opportunity* this opens must be claimed honestly: detectable ≠ fully reconstructable.
4. **Overfitting tiny subject pools / leakage.** With only 9 subjects, within-subject train/test splits and epoch-level shuffles inflate scores via identity and temporal-autocorrelation leakage. The credible design holds out **whole subjects** (LOSO) and reports the generalization gap explicitly. This is the single most likely way a first claim could look like a success and not be one — it must be pre-declared as a non-transfer guard.
5. **Reporting a single scalar hides band/region structure.** Reconstruction work that collapses to one correlation number obscures that low-frequency/coupled components are recoverable while high-frequency/local components are not. Per-band, per-region reporting prevents over-claiming.

---

## 5. Open questions (feeding Slot 3 — the transferable claim)

The field leaves clear gaps this project could address as a first rung. Candidate first-claim directions, roughly ordered easier → harder:

- **A. Scalp-only decoding of a deep-validated WM state.** Decode working-memory load (set size) and/or hippocampal-coupling magnitude from scalp EEG *single-trial*, and validate that the scalp-derived estimate tracks the simultaneously recorded iEEG/MTL ground truth (theta-alpha coupling, persistent firing). Novelty: single-trial, scalp-only, with intracranial validation — unestablished for this dataset. Lowest risk; strong verification artifact.
- **B. Scalp→MTL band-power time-course reconstruction.** Reconstruct the *time course of MTL iEEG band power* (e.g., theta) from scalp EEG, validated by correlation against true iEEG band power on held-out subjects. A focused, honest slice of the NeuroFlowNet framing aimed at the band the coupling literature says is recoverable.
- **C. Scalp→iEEG waveform reconstruction (MTL).** The fullest NeuroFlowNet-style target. Highest overlap with existing 2026 work; would need a clear differentiator (units/LFP targets, efficiency on 8 GB, or rigorous LOSO generalization the prior work may not stress).
- **D. Reaching toward population firing.** Predict MTL population-firing-rate envelopes (from the unit data) from scalp EEG. Uses the dataset's rarest asset; hardest and likely a *later* rung, but worth naming as the staircase's direction.

**Cross-cutting open questions the Claim Sheet must answer:** Which scalp channels/bands carry the most deep information (Fedele points at P3/theta)? How much does performance degrade subject-to-subject (the affordability-relevant question — a consumer tool must generalize)? Can a physics-informed prior (leadfield-aware) beat a purely data-driven net on *this much* data? What is the smallest model that meets the bar on 8 GB VRAM?

My current lean (to debate with Codex in Phase 1): **direction A or B** is the right first rung — each yields a sharp, intracranially-validated, single-sentence claim; each fits the compute envelope; each builds infrastructure (data loading, alignment, LOSO harness, validation metrics) that any later rung (C, D) reuses; and each differentiates cleanly from NeuroFlowNet by foregrounding *deep-state validation* over raw waveform mimicry.

---

## 6. References

Full entries are maintained in `agents/Claude/references.md` (same format, migrated this session). Key load-bearing sources:

- Boran E. et al. (2020). *Dataset of human MTL neurons, scalp and intracranial EEG during a verbal working memory task.* Scientific Data 7:30. DOI 10.1038/s41597-020-0364-3.
- Boran E. et al. (2019). *Persistent hippocampal neural firing and hippocampal-cortical coupling predict verbal working memory load.* Science Advances 5(3):eaav3687. DOI 10.1126/sciadv.aav3687.
- Fedele T. et al. (2020). *Functional synchronization between hippocampal sEEG, parietal ECoG and scalp EEG during a verbal working memory task.* bioRxiv 2020.06.05.136515.
- NeuroFlowNet (2026). *Non-Invasive Reconstruction of Intracranial EEG Across the Deep Temporal Lobe from Scalp EEG based on Conditional Normalizing Flow.* arXiv:2603.03354.
- DL subcortical M/EEG source localization with realistic head model. APL Bioengineering 8(4):046104 (2024) / bioRxiv 2024.04.30.591970.
- 3D-PIUNet (2024). *Enhancing Brain Source Reconstruction by Initializing 3D Neural Networks with Physical Inverse Solutions.* arXiv:2411.00143.
- Vorwerk J. et al. (2019). *Influence of Head Tissue Conductivity Uncertainties on EEG Dipole Reconstruction.* Frontiers in Neuroscience 13:531. DOI 10.3389/fnins.2019.00531.
- Jiang W.-B. et al. (2024). *LaBraM: Large Brain Model for Learning Generic Representations with Tremendous EEG Data in BCI.* ICLR 2024. arXiv:2405.18765.
- Constantino et al. (2021). *Deep Learning of Simultaneous Intracranial and Scalp EEG for Prediction, Detection, and Lateralization of Mesial Temporal Lobe Seizures.* Frontiers in Neurology 12:705119 (PMC8632629).
- Roehri N. et al. *Scalp-negative medial temporal interictal epileptic discharges alter large-scale brain networks.* Epilepsia. DOI 10.1002/epi.70061.
- *Manifestation of hippocampal interictal discharges on clinical scalp EEG recordings.* PMC8590709.
- *Inferring entire spiking activity from local field potentials with deep learning.* bioRxiv 2020.05.02.074104.
