# Codex References

This file records sources that informed Codex's Phase 0 work on the EEG-to-LFP project. Entries emphasize how each source shapes project decisions, not just what it says.

## Dataset and licensing

### Boran et al. simultaneous scalp EEG/iEEG/MTL unit dataset

Summary: Public G-Node GIN dataset containing simultaneous 10-20 scalp EEG, depth iEEG/LFP, 1526 MTL units, electrode coordinates/anatomical labels, and verbal working-memory task metadata from 9 epilepsy patients.

Project use: This is the validation substrate for the whole project. Its subject count and session structure drive the recommendation for subject-held-out evaluation, region-level target construction, and careful leakage controls.

Link: https://gin.g-node.org/USZ_NCH/Human_MTL_units_scalp_EEG_and_iEEG_verbal_WM

Citation: Boran, E., Fedele, T., Steiner, A., Hilfiker, P., Stieglitz, L., Grunwald, T., & Sarnthein, J. (2019). Dataset of simultaneous scalp EEG and intracranial EEG recordings and human medial temporal lobe units during a verbal working memory task. G-Node. https://doi.org/10.12751/g-node.d76994

### Creative Commons Attribution-ShareAlike 4.0 International

Summary: The dataset license permits reuse, including commercial reuse, but requires attribution and ShareAlike treatment for shared adapted material. The legal code also describes sui generis database-right obligations.

Project use: Informed the Phase 0 recommendation to keep raw data out of the repository, preserve attribution, and treat released derived datasets or trained weights as license-sensitive until Phase 1 decides a release policy.

Link: https://creativecommons.org/licenses/by-sa/4.0/legalcode.en

Citation: Creative Commons. (n.d.). Attribution-ShareAlike 4.0 International legal code. https://creativecommons.org/licenses/by-sa/4.0/legalcode.en

## Working-memory and MTL physiology

### Persistent hippocampal firing and hippocampal-cortical coupling

Summary: Reports that persistent hippocampal neural firing and hippocampal-cortical coupling predict verbal working-memory load in the dataset's task context.

Project use: Provides the main biological reason to prefer a first-rung claim about deep-state or coupling-signature decoding over generic waveform reconstruction.

Link: https://doi.org/10.1126/sciadv.aav3687

Citation: Boran, E., Fedele, T., Klaver, P., Hilfiker, P., Stieglitz, L., Grunwald, T., & Sarnthein, J. (2019). Persistent hippocampal neural firing and hippocampal-cortical coupling predict verbal working memory load. Science Advances, 5(3), eaav3687. https://doi.org/10.1126/sciadv.aav3687

## Scalp EEG to intracranial reconstruction

### NeuroFlowNet

Summary: Recent conditional normalizing-flow approach for reconstructing MTL iEEG from scalp EEG. The paper reports band-limited waveform, PSD, alpha-power, and inter-channel correlation fidelity on a public synchronized EEG-iEEG dataset under a subject-specific protocol. Reported functional-connectivity errors favored NeuroFlowNet over linear, shallow CNN, 1D U-Net, and tiny Transformer baselines.

Project use: Establishes close prior art and warns that Dandelion should differentiate on deep-state validation, subject-held-out generalization, and modest first-rung claims. It also suggests metrics for later reconstruction diagnostics.

Link: https://arxiv.org/abs/2603.03354

Citation: He, D., Jiang, B., Feng, K., Zhang, L., Liu, L., Li, Y., Zhao, Y., & Yan, H. (2026). Non-invasive reconstruction of intracranial EEG across the deep temporal lobe from scalp EEG based on conditional normalizing flow. arXiv:2603.03354. https://doi.org/10.48550/arXiv.2603.03354

## EEG model choices and validation

### EEGNet

Summary: Compact convolutional neural network for multiple EEG-based BCI paradigms using depthwise and separable convolutions, designed to work with limited EEG data and interpretable learned features.

Project use: Appropriate as a later compact neural baseline if simple regularized and covariance models clear their initial gates. Not recommended as the first model to run.

Link: https://arxiv.org/abs/1611.08024

Citation: Lawhern, V. J., Solon, A. J., Waytowich, N. R., Gordon, S. M., Hung, C. P., & Lance, B. J. (2016). EEGNet: A compact convolutional network for EEG-based brain-computer interfaces. arXiv:1611.08024. https://arxiv.org/abs/1611.08024

### LaBraM

Summary: EEG foundation model trained on about 2500 hours from around 20 datasets using channel-patch tokenization and masked neural-code prediction. The GitHub repository is MIT-licensed, but recommended full pretraining uses multi-GPU hardware far beyond this project.

Project use: Supports keeping foundation-model transfer as an optional later comparison rather than the first rung. Pretrained checkpoint provenance and license compatibility should be checked before any use.

Links: https://arxiv.org/abs/2405.18765 and https://github.com/935963004/LaBraM

Citation: Jiang, W.-B., Zhao, L.-M., & Lu, B.-L. (2024). Large Brain Model for Learning Generic Representations with Tremendous EEG Data in BCI. International Conference on Learning Representations. https://openreview.net/forum?id=QzTpTRVtrP

### EEG foundation-model feature audit

Summary: Audits what three EEG foundation models capture and reports that a large share of model advantage can be explained by known hand-crafted feature families, especially frequency-domain features.

Project use: Reinforces the recommendation to start with transparent frequency, covariance, and coupling features before introducing foundation models.

Link: https://arxiv.org/abs/2605.11410

Citation: Tang, L., Chen, Q., Mei, J., Xu, H., Zhang, Q., Shao, J., Zou, N., Hu, X., & Liu, D. (2026). What do EEG foundation models capture from human brain signals? arXiv:2605.11410. https://doi.org/10.48550/arXiv.2605.11410

### EEG foundation-model leakage audit

Summary: Reports that released EEG foundation embeddings can leak spectral attributes across encoder families under a cross-encoder transfer audit.

Project use: Adds privacy and release-risk weight against using pretrained EEG foundation embeddings as the initial route for a project whose long-term purpose is affordable and responsible public technology.

Link: https://arxiv.org/abs/2606.09189

Citation: Tai, J. (2026). Pretrained, frozen, still leaking: Auditing cross-encoder attribute transfer in EEG foundation models. arXiv:2606.09189. https://doi.org/10.48550/arXiv.2606.09189

### EEG partitioning and cross-subject evaluation

Summary: Recent EEG deep-learning partitioning study emphasizing that subject-based cross-validation is important for reliable cross-subject analysis and that non-nested strategies can leak validation information.

Project use: Supports making subject-held-out evaluation and inner-loop tuning hard requirements for the headline claim.

Link: https://arxiv.org/abs/2505.13021

Citation: Del Pup, F., Zanola, A., Tshimanga, L. F., Bertoldo, A., Finos, L., & Atzori, M. (2025). The role of data partitioning on the performance of EEG-based deep learning models in supervised cross-subject analysis: A preliminary study. arXiv:2505.13021. https://arxiv.org/abs/2505.13021

### Brain decoder cross-validation guidelines

Summary: Reviews cross-validation caveats for brain decoding, including circularity risk, hyperparameter tuning, and large error bars in small neuroimaging datasets.

Project use: Informs the recommendation to use sane defaults where possible, nested tuning where needed, and uncertainty intervals rather than single aggregate scores.

Link: https://arxiv.org/abs/1606.05201

Citation: Varoquaux, G., Raamana, P. R., Engemann, D. A., Hoyos-Idrobo, A., Schwartz, Y., & Thirion, B. (2016). Assessing and tuning brain decoders: Cross-validation, caveats, and guidelines. arXiv:1606.05201. https://arxiv.org/abs/1606.05201

### Riemannian geometry for EEG classification

Summary: Information-geometry approaches classify EEG covariance structure with comparatively low calibration demand and good cross-session/subject behavior in BCI settings.

Project use: Supports including a Riemannian covariance model as a small-data diagnostic after simpler regularized models.

Link: https://arxiv.org/abs/1409.0107

Citation: Barachant, A., & Congedo, M. (2014). A plug&play P300 BCI using information geometry. arXiv:1409.0107. https://arxiv.org/abs/1409.0107

## EEG inverse/source-localization background

### Bayesian EEG source imaging and depth bias

Summary: Reviews Bayesian solvers for EEG distributed source imaging and highlights depth bias, ill-posedness, prior selection, and the need for depth weighting when deeper sources are considered.

Project use: Supports the core Phase 0 caution that scalp EEG to MTL work should not start as direct field/source recovery.

Link: https://arxiv.org/abs/2604.05913

Citation: Lahtinen, J., & Koulouri, A. (2026). Overview of Bayesian solvers in EEG distributed source models: Prior selection, algorithmic implementation, and depth bias reduction. arXiv:2604.05913. https://arxiv.org/abs/2604.05913
