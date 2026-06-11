# references.md — Claude

Running bibliography for the EEG → deep/MTL activity project. Every entry below was located via live web search and carries a working link or DOI. At Phase 2 these are reconciled with Codex's `references.md` into the Technical Report bibliography.

Format per entry: **Citation** · *What it covers / why it matters* · *How it informed the project* · Link/DOI.

---

### Primary dataset

**Boran, E., Fedele, T., Steiner, A., Hilfiker, P., Stieglitz, L., Grunwald, T., Sarnthein, J. (2020). Dataset of human medial temporal lobe neurons, scalp and intracranial EEG during a verbal working memory task. *Scientific Data*, 7, 30.**
- *Covers:* The project's primary dataset — 9 epilepsy patients, modified Sternberg verbal WM task; simultaneous scalp EEG (10–20), iEEG depth electrodes, 1526 MTL single units, MNI coordinates/anatomical labels, trial metadata. NIX/HDF5 format, CC BY-SA 4.0.
- *Informed:* Defines the entire substrate and the source of simultaneous ground truth that makes the project verifiable. Sets format, validation design, and licensing baseline.
- DOI: 10.1038/s41597-020-0364-3 · https://www.nature.com/articles/s41597-020-0364-3 · G-Node: 10.12751/g-node.d76994

### Mechanism: scalp ↔ deep coupling in this paradigm

**Boran, E., et al. (2019). Persistent hippocampal neural firing and hippocampal-cortical coupling predict verbal working memory load. *Science Advances*, 5(3), eaav3687.**
- *Covers:* WM load ↑ → persistent hippocampal unit firing ↑ and hippocampus–cortex theta–alpha synchronization ↑.
- *Informed:* Mechanistic backbone — establishes the oscillatory coupling channel by which deep activity could leave a scalp signature; motivates candidate first-claim directions A/B and the theta-alpha target band.
- DOI: 10.1126/sciadv.aav3687 · https://www.science.org/doi/full/10.1126/sciadv.aav3687

**Fedele, T., et al. (2020). Functional synchronization between hippocampal sEEG, parietal ECoG and scalp EEG during a verbal working memory task. *bioRxiv* 2020.06.05.136515.**
- *Covers:* Direct measurement of hippocampal-sEEG ↔ scalp-EEG phase locking; WM maintenance enhances theta (~6–7 Hz) PLV to left parietal P3.
- *Informed:* Near-direct evidence that scalp channels carry a measurable deep-MTL coupling trace in this exact data; points at specific channels/bands (P3, theta) to weight in features/targets.
- DOI: 10.1101/2020.06.05.136515 · https://www.biorxiv.org/content/10.1101/2020.06.05.136515v1.full

### Closest prior art: scalp → intracranial reconstruction

**NeuroFlowNet (2026). Non-Invasive Reconstruction of Intracranial EEG Across the Deep Temporal Lobe from Scalp EEG based on Conditional Normalizing Flow. *arXiv:2603.03354*.**
- *Covers:* Conditional normalizing flow w/ multi-scale + self-attention; "first reconstruction of iEEG across entire deep temporal lobe from scalp EEG"; validated on waveform fidelity, spectral reproduction, functional-connectivity restoration using a public synchronized sEEG–iEEG dataset.
- *Informed:* Proves the signal-to-signal framing is tractable and publishable; defines the differentiation pressure on our first claim (avoid pure waveform mimicry; foreground deep-state validation, LOSO generalization, or efficiency). **Action: extract numeric metrics + confirm which dataset from full PDF in Phase 1.**
- https://arxiv.org/abs/2603.03354

### Deep-learning source imaging (learned inverse)

**DL subcortical + cortical M/EEG source localization with realistic head conductivity model. *APL Bioengineering* 8(4), 046104 (2024); preprint bioRxiv 2024.04.30.591970.**
- *Covers:* CNN localizing cortical AND subcortical sources using a realistic head model; validated against simulation, evoked potentials, and invasive recordings.
- *Informed:* Demonstrates DL can target subcortical sources and sets the credibility bar (validate against invasive ground truth — which we have).
- https://pubs.aip.org/aip/apb/article/8/4/046104/3318292 · https://www.biorxiv.org/content/10.1101/2024.04.30.591970.full.pdf

**Enhancing Brain Source Reconstruction by Initializing 3D Neural Networks with Physical Inverse Solutions (3D-PIUNet). *arXiv:2411.00143*.**
- *Covers:* Hybrid — physics-informed pseudo-inverse initial estimate refined by a 3D U-Net data prior.
- *Informed:* Template for a physics-informed component (the director's "PINN" intuition) that respects the forward model without trusting it as exact.
- https://arxiv.org/pdf/2411.00143

**Vorwerk, J., et al. (2019). Influence of Head Tissue Conductivity Uncertainties on EEG Dipole Reconstruction. *Frontiers in Neuroscience*, 13, 531.**
- *Covers:* Sensitivity of EEG source estimates to skull/tissue conductivity uncertainty; cost of leadfield computation.
- *Informed:* Failure mode #2 — any physics-informed prior must treat the head model as uncertain, not exact.
- DOI: 10.3389/fnins.2019.00531 · https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00531/full

### Scalp detectability of deep/MTL events (the central bet, and its limits)

**Constantino, A.C., et al. (2021). Deep Learning of Simultaneous Intracranial and Scalp EEG for Prediction, Detection, and Lateralization of Mesial Temporal Lobe Seizures. *Frontiers in Neurology*, 12, 705119.**
- *Covers:* CNN classifies seizure/pre-seizure/non-seizure epochs >98%; surface-negative mesial-temporal seizures invisible to human readers still detected/lateralized by ML.
- *Informed:* Upper-bound evidence that scalp EEG carries decodable deep-origin information even when expert reading says otherwise — the project's central bet.
- https://pmc.ncbi.nlm.nih.gov/articles/PMC8632629/

**Roehri, N., et al. Scalp-negative medial temporal interictal epileptic discharges alter large-scale brain networks: a simultaneous HD-EEG and iEEG study. *Epilepsia*.**
- *Covers:* Scalp-negative MTL discharges still perturb large-scale cortical networks.
- *Informed:* Failure mode #3 — "invisible to the eye" ≠ "absent from signal"; deep events have distributed cortical (hence scalp-reachable) signatures.
- DOI: 10.1002/epi.70061 · https://onlinelibrary.wiley.com/doi/10.1002/epi.70061

**Manifestation of hippocampal interictal discharges on clinical scalp EEG recordings. (PMC8590709.)**
- *Covers:* Only a small fraction of hippocampal IEDs appear on scalp; volume conduction + synaptic propagation both contribute.
- *Informed:* Honest bound on the opportunity — detectable does not mean fully reconstructable; sets expectations for what a first claim can promise.
- https://pmc.ncbi.nlm.nih.gov/articles/PMC8590709/

### Representation learning / foundation models (small-data transfer)

**Jiang, W.-B., Zhao, L.-M., Lu, B.-L. (2024). LaBraM: Large Brain Model for Learning Generic Representations with Tremendous EEG Data in BCI. *ICLR 2024* (spotlight). arXiv:2405.18765.**
- *Covers:* Neural-tokenizer + masked EEG modeling on ~2,500 h; cross-dataset channel-patch representation.
- *Informed:* Candidate transfer backbone to extract more from 9 subjects than training from scratch; **license + 8 GB VRAM fit to verify before adoption.**
- https://arxiv.org/abs/2405.18765 · code: https://github.com/935963004/LaBraM

### Below iEEG: LFP ↔ spikes

**Inferring entire spiking activity from local field potentials with deep learning. *bioRxiv* 2020.05.02.074104.**
- *Covers:* DL maps LFP → spiking activity.
- *Informed:* Supports the hardest/later rung (D) — reaching toward MTL population firing using the dataset's unit data.
- https://www.biorxiv.org/content/10.1101/2020.05.02.074104.full.pdf

### Tools / software (data layer, Phase 2)

**G-Node NIX / `nixio` (Python), v1.5.4. BSD-licensed.**
- *Covers:* NIX is a standardized data model on top of HDF5; `nixio` is the official Python reader. The dataset ships one NIX `.h5` per session (blocks of per-trial DataArrays, metadata sections, event SingleTags, electrode Sources).
- *Informed:* The reader (`utils/nix_io.py`) is built on `nixio`. One quirk drove a design choice: these files use NIX's legacy "old values" metadata format and `nixio` decodes char properties strictly as UTF-8, which crashes on German place-names in the General/Task sections — isolated via a per-property safe-read so a single non-UTF8 field can't take down a whole-session read. License (BSD) permits commercial use.
- https://github.com/G-Node/nixpy · https://nixio.readthedocs.io

### Background / context (consulted, lighter weight)

**What is the Relationship Between Scalp EEG, Intracranial EEG, and Microelectrode Activities? Springer (2023), chapter.**
- *Covers:* Review of cross-scale electrophysiology relationships.
- *Informed:* General grounding on the three-depth signal hierarchy the dataset spans.
- https://link.springer.com/chapter/10.1007/978-3-031-20910-9_16

**EEG foundation-model landscape (EEGPT; CBraMod, ICLR 2025; systematic review arXiv:2602.03269).**
- *Covers:* Self-supervised transformer/SSM EEG encoders, masked + contrastive pretraining.
- *Informed:* Menu of transfer backbones and the state of the small-data transfer art; revisit at Phase 1 for license/compute fit.
- https://arxiv.org/pdf/2602.03269
