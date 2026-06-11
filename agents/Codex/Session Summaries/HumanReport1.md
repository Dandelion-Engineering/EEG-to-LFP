# Human Report 1 - Codex

**Date/Time:** 2026-06-11 06:13 PDT
**Agent:** Codex
**Session:** 1
**Phase:** 0 - Literature Review / Alignment

## Summary

This was Codex's first working session in the current repository state. I followed `AgentPrompt.md`: checked the session lock, created `.codex-session.lock`, read the project details, reviewed Codex's empty workspace, read the active Claude-Codex Phase 0 chat, inspected the local dataset metadata at `D:\Simultaneous EEG_LFP`, wrote Codex's Phase 0 foundation and references, compared against Claude's Session 1 work, and appended Codex's alignment response to the active chat.

Phase 0 is not formally closed yet. Codex has completed its side of Phase 0, but the Claude-Codex alignment chat remains active until Claude accepts the convergence or writes the closure summary.

## What was accomplished

1. **Established Codex's Phase 0 position.**

   I wrote `agents/Codex/Literature Foundation.md`. The key recommendation is that the first project should not claim direct MTL field recovery from scalp EEG. It should test a smaller, cleaner claim: whether scalp EEG contains a subject-transferable signature of an intracranially validated MTL working-memory state.

2. **Created Codex's references file.**

   I wrote `agents/Codex/references.md` with citation-ready entries and project-use notes. The references include the public G-Node dataset, Boran et al. 2019, NeuroFlowNet, CC BY-SA 4.0, EEGNet, LaBraM, EEG foundation-model audits, cross-validation guidance, Riemannian EEG classification, and EEG source-imaging background.

3. **Inspected the local dataset enough to ground feasibility.**

   The dataset is present at `D:\Simultaneous EEG_LFP`. It includes 37 NIX/HDF5 session files across 9 subjects, MATLAB loading code, README metadata, a CC BY-SA 4.0 license, and subject/file-structure PDFs. The project `venv` currently lacks core analysis packages such as NumPy, SciPy, h5py, MNE, and scikit-learn, so Phase 1 implementation will need explicit dependency setup and pinned versions.

4. **Answered Claude's NeuroFlowNet question.**

   I reviewed the full NeuroFlowNet paper enough to extract the practical details Claude asked for:

   - It uses the same public synchronized EEG/iEEG verbal working-memory dataset family.
   - Its reported public-dataset experiments use Subjects S1, S6, and S9.
   - It is subject-specific, with each subject trained separately under a 90%/10% trial split.
   - It is therefore not a leave-one-subject-out benchmark.
   - Its alpha-band functional-connectivity relative-error table reports NeuroFlowNet as best: S1 0.163, S6 0.166, S9 0.141, mean 0.157.
   - The paper reports training on one RTX 4080 with 16 GB VRAM, above this project's 8 GB laptop-GPU envelope.

5. **Updated the active Claude-Codex chat.**

   I appended Codex's response to `chats/Claude-Codex/Phase 0 Literature Alignment/Phase 0 Literature Alignment - Active.md`. Codex agrees with Claude on the main frame: coupling-signature or deep-state decoding first, Candidate A as the first rung, Candidate B as a fast-follow, LOSO as a core success/failure guard, and foundation models deferred until after transparent baselines.

6. **Updated Codex workspace navigation.**

   I populated `agents/Codex/README.md` so future agents can quickly see which files are authoritative and where the active co-owned chat lives.

## Important decisions

- **Preferred first rung:** Candidate A, scalp-only prediction of an intracranially validated working-memory/deep-state target.
- **Fast-follow:** Candidate B, scalp-to-MTL theta/alpha band-power time-course reconstruction.
- **Headline evaluation:** leave-one-subject-out or another subject-held-out protocol. Within-subject results can be diagnostic only.
- **Target hygiene:** if "coupling magnitude" is used as a target, do not define that target from the same scalp channels used as predictors. The cleanest first Claim Sheet may use working-memory load as the primary target and iEEG/unit coupling as the mechanistic validation layer.
- **Licensing:** CC BY-SA is manageable but real. Raw data should not be redistributed in the repo. Derived datasets and possibly model weights should be treated as ShareAlike-sensitive until the Claim Sheet records a policy.
- **Models:** start with hand-crafted band/covariance/coupling features and simple regularized models. EEGNet, Riemannian models, and foundation models are optional later comparisons, not the first move.

## Challenges and how they were handled

- The local `pdftotext` utility failed because MiKTeX is misconfigured. I used primary web sources and local dataset text metadata instead.
- The project `venv` is minimal, so no HDF5 introspection was done through Python. I used the included dataset README and MATLAB loader to understand the data structure without installing dependencies during Phase 0.
- Codex's automation memory mentioned older Codex artifacts and a different apparent state, but the current `main` branch only contained Claude's Session 1 work and empty Codex files. I treated the repository state as authoritative and created Codex Session 1 artifacts fresh.

## Files created or updated

- `agents/Codex/Literature Foundation.md`
- `agents/Codex/references.md`
- `agents/Codex/README.md`
- `agents/Codex/Summary of Only Necessary Context.md`
- `agents/Codex/Session Summaries/HumanReport1.md`
- `chats/Claude-Codex/Phase 0 Literature Alignment/Phase 0 Literature Alignment - Active.md`

## Next steps

1. Claude should read Codex's Literature Foundation and chat reply.
2. If Claude agrees, Claude should close the Phase 0 alignment chat and write the Phase 0 closure summary/report required by the project framework.
3. Phase 1 should draft the technical Claim Sheet around Candidate A, with Candidate B as fast-follow.
4. Phase 1 should define the exact target construction, LOSO split, controls, metrics, dependency stack, and CC BY-SA handling before any analysis code is written.

Nothing is blocked on Randy yet. The first likely director-facing request remains Claim Sheet review after Phase 1 drafting.
