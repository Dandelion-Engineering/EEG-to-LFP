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

### Methods: covariance / Riemannian decoding (Phase 2 feature layer)

**Barachant, A., Bonnet, S., Congedo, M., Jutten, C. (2012). Multiclass Brain-Computer Interface Classification by Riemannian Geometry. *IEEE Transactions on Biomedical Engineering*, 59(4), 920–928.**
- *Covers:* Uses spatial covariance matrices as EEG descriptors and classifies them on the manifold of symmetric positive-definite (SPD) matrices. Introduces *tangent-space* classification: map covariances onto the tangent space at the Fréchet mean via the matrix logarithm, vectorize, and feed to an ordinary Euclidean classifier (LDA/logistic/SVM) with little loss vs. the full Riemannian distance.
- *Informed:* The `covariance` feature family in `utils/features.py` is exactly this — per-band shrunk channel covariances, matrix-logged and vech-vectorized into a flat, ML-ready representation that a logistic/LDA baseline can consume now and a Riemannian rung can use later. On the 8-channel common montage this lifted rung-1 LOSO balanced accuracy from 0.512 (band power only) to 0.560 (covariance/all). Justifies the model-ladder ordering (logistic/LDA → filter-bank covariance + shrinkage → Riemannian).
- DOI: 10.1109/TBME.2011.2172210 · https://pubmed.ncbi.nlm.nih.gov/22010143/ · full text: https://hal.science/hal-00681328v1/document
- *Session 6 update:* Built the explicit Riemannian rungs (`utils/riemann.py`, `scripts/run_riemann_decoder.py`). Rung 2 (filter-bank tangent space referenced to the per-band training Fréchet mean) and rung 3 (minimum distance to per-class Riemannian means) both landed at 0.533–0.558 mean LOSO balanced accuracy — no gain over rung 1's 0.560, and none beats the behavioral-only control (0.593). The linear→Riemannian model-class axis is exhausted here without clearing the success bar; the binding constraint is the 8-channel montage + cross-subject transfer, not the model class.

**Zanini, P., Congedo, M., Jutten, C., Said, S., Berthoumieu, Y. (2018). Transfer Learning: A Riemannian Geometry Framework With Applications to Brain–Computer Interfaces. *IEEE Transactions on Biomedical Engineering*, 65(5), 1107–1116.**
- *Covers:* Cross-session/cross-subject transfer by *recentering* — affine-transforming each session/subject's SPD covariances so they are centered on a common reference (the identity, via whitening by that session/subject's own Riemannian mean), which removes subject-specific offsets and makes covariances comparable across people. The recentering uses only the unlabeled covariances, so it is an unsupervised domain-alignment step.
- *Informed:* The `--recenter` option in `run_riemann_decoder.py`. It rescued rung-3 MDM from collapse (without it, MDM predicted a single class for 6/9 held-out subjects, mean 0.533; with per-subject recentering, 0.545 and no collapse). Applied transductively to the held-out subject's own inputs only — no held-out *label* is ever touched, so the held-out-once discipline holds. Did not lift the headline mean, which confirms the plateau is a signal/montage ceiling rather than a domain-shift artifact.
- DOI: 10.1109/TBME.2017.2742541 · https://pubmed.ncbi.nlm.nih.gov/28841546/ · full text: https://hal.science/hal-01923278

### Methods: compact CNN decoding (Phase 2, rung 4)

**Lawhern, V.J., Solon, A.J., Waytowich, N.R., Gordon, S.M., Hung, C.P., Lance, B.J. (2018). EEGNet: a compact convolutional neural network for EEG-based brain–computer interfaces. *Journal of Neural Engineering*, 15(5), 056013.**
- *Covers:* A small, general-purpose CNN for EEG that learns spatiotemporal filters directly from the raw multichannel waveform. Architecture: a temporal convolution (learns frequency filters) → a depthwise spatial convolution grouped per temporal filter (learns spatial/channel weightings, like learned spatial filters) → a separable convolution (depthwise temporal + pointwise mixing) → a small dense classifier. Designed to work with few trials and few parameters relative to generic deep nets.
- *Informed:* The basis for rung 4 of the decoding ladder. I implemented it dependency-free in NumPy (`utils/eegnet.py`; F1=8, D=2, F2=16, temporal kernels 64 then 16, average-pool 4 then 8) because the environment couldn't host a deep-learning framework and the network is tiny — same hand-rolled precedent as `utils/riemann.py`. Full finite-difference gradient check passes (max relative error ~5e-6). Driver `scripts/run_eegnet_decoder.py` runs it LOSO on the locked 8-channel montage's raw maintenance-window epochs, aligned to the same kept trials as rungs 1–3. **Session 8 result:** mean LOSO balanced accuracy 0.616 — the only rung to beat the behavioral-only control (0.593) on the mean, but it fails the headline bar (improvement +0.023; 5/9 subjects; the positive mean rests entirely on one subject, S04 +0.218, so it fails the single-subject-removal robustness criterion). Completes the pre-registered model-class ladder as a clean negative; the binding constraint is confirmed to be the 8-channel montage + cross-subject transfer, not the model class.
- DOI: 10.1088/1741-2552/aace8c · https://iopscience.iop.org/article/10.1088/1741-2552/aace8c · preprint: https://arxiv.org/abs/1611.08024

### Background / context (consulted, lighter weight)

**What is the Relationship Between Scalp EEG, Intracranial EEG, and Microelectrode Activities? Springer (2023), chapter.**
- *Covers:* Review of cross-scale electrophysiology relationships.
- *Informed:* General grounding on the three-depth signal hierarchy the dataset spans.
- https://link.springer.com/chapter/10.1007/978-3-031-20910-9_16

**EEG foundation-model landscape (EEGPT; CBraMod, ICLR 2025; systematic review arXiv:2602.03269).**
- *Covers:* Self-supervised transformer/SSM EEG encoders, masked + contrastive pretraining.
- *Informed:* Menu of transfer backbones and the state of the small-data transfer art; revisit at Phase 1 for license/compute fit.
- https://arxiv.org/pdf/2602.03269
