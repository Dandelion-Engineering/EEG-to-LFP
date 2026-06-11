# Summary of Only Necessary Context - Codex

**Last rewritten:** 2026-06-11 (Codex Session 2)
**Current phase:** Phase 1 - Claim Sheet Review active; technical Claim Sheet not yet approved

Re-read `AgentPrompt.md` and `Project Details/Project Details.md` at the start of the next session. This file only records Codex-specific continuity not already contained there.

## Current project state

Phase 0 is closed. Claude closed the Phase 0 literature alignment chat during Codex Session 2 and wrote:

- `chats/Claude-Codex/Phase 0 Literature Alignment/Phase 0 Literature Alignment - Concluded.md`
- `chats/Claude-Codex/Phase 0 Literature Alignment/Summary.md`

The project is now in Phase 1. Claude drafted the technical Claim Sheet at:

- `Claim Sheet.md`

Claude also opened the active Phase 1 review chat:

- `chats/Claude-Codex/Claim Sheet Phase 1/Claim Sheet Phase 1 - Active.md`

Codex reviewed the draft Claim Sheet in Session 2 and appended a review to the Phase 1 chat. Codex has **not** approved the Claim Sheet yet.

## Codex workspace state

Codex workspace files now include:

- `agents/Codex/Literature Foundation.md` - Codex's Phase 0 scientific foundation.
- `agents/Codex/references.md` - Codex's running bibliography.
- `agents/Codex/Phase 1 Claim Sheet Review Scaffold.md` - Codex's checklist for reviewing the Phase 1 Claim Sheet.
- `agents/Codex/README.md` - workspace navigation, updated to include the scaffold.
- `agents/Codex/Session Summaries/HumanReport1.md`
- `agents/Codex/Session Summaries/HumanReport2.md`

## Phase 0 alignment outcome

Claude and Codex converged on the same first-rung framing:

- The project should be framed as coupling-signature or deep-state decoding, not direct MTL field recovery from scalp EEG.
- Candidate A is the first rung: scalp-only prediction of an intracranially validated working-memory/deep-state target.
- Candidate B is the fast-follow: scalp-to-MTL theta/alpha band-power time-course reconstruction.
- Leave-one-subject-out or otherwise subject-held-out evaluation is the headline.
- Within-subject results are diagnostic only.
- Foundation models are deferred; transparent hand-crafted features and compact models come first.
- NeuroFlowNet is prior art and context, not the implementation template.

The accepted target-hygiene refinement is:

- Primary target: working-memory load / set size, independent of neural channels.
- Mechanism-validation layer: iEEG theta-alpha coupling and MTL unit firing.
- Predeclared extension: predict an intracranially defined coupling state from scalp-only features if the primary clears its gate.

## Codex Claim Sheet review status

Codex told Claude the draft is strong but requires amendments before approval.

Required amendments:

1. **Behavioral-only control label leakage.** The behavioral-only control must explicitly exclude set size and any derived variable that encodes set size, because set size is the primary target. It may use response time, correctness, match/mismatch, session, trial order, and timing variables that do not encode the label.
2. **Primary epoch.** The headline should be maintenance-period decoding. Encoding-period decoding risks reading sensory stimulus-load cues rather than maintained working-memory state. Encoding and retrieval can be secondary diagnostics.
3. **Concrete success/statistics rule.** Codex proposed primary binary high-vs-low load classification, set size 4 versus 6/8, LOSO balanced accuracy during maintenance, at least +0.075 absolute improvement over the strongest non-signal control, at least 7 of 9 held-out subjects above that control, and no single-subject dependence. Window-level permutation must not substitute for subject-level evidence.
4. **Mechanism-layer coverage downgrade.** If at least 5 subjects have adequate MTL coverage, the mechanism layer can support the full deep-readout claim. If fewer than 5 qualify, the result should be downgraded to load decoding with mechanism evidence too sparse or inconclusive.

Codex accepts the draft's high-level claim, Candidate A primary / Candidate B fast-follow structure, licensing policy, model ladder, and general division of labor once the amendments are made.

## Recommended next Codex action

At the start of Codex Session 3:

1. Read the active Phase 1 chat.
2. Check whether Claude amended `Claim Sheet.md`.
3. If amended, verify the four required changes above.
4. If resolved, approve the technical Claim Sheet in the chat.
5. If not resolved, reply with the remaining blockers.

Do not begin Phase 2 implementation until the technical Claim Sheet is approved and the Accessible Claim Sheet / director review path exists.

## Local substrate facts to carry forward

- Dataset path: `D:\Simultaneous EEG_LFP`
- Local dataset files include 37 session `.h5` files in `data_nix`, MATLAB loading code, README metadata, `datacite.yml`, a CC BY-SA license, and subject/file-structure PDFs.
- Dataset summary from local metadata: 9 epilepsy patients, modified Sternberg verbal working-memory task, simultaneous 10-20 scalp EEG, depth iEEG/LFP, 1526 MTL units, MNI coordinates/anatomical labels, and trial metadata.
- The project virtual environment exists at `.\venv` and uses Python 3.11.9, but currently lacks core dependencies such as NumPy, SciPy, h5py, MNE, scikit-learn, nixio, and torch.
- For all Python work, use only `.\venv\Scripts\python.exe` and `.\venv\Scripts\pip.exe`.

## Process reminders

- Codex Session 3 should create `HumanReport3.md`; do not overwrite earlier reports.
- Codex progress report is due at Session 8 unless a phase transition or approved amendment requires an earlier progress report.
- Active chat files must only be appended to.
- Claude is the default writer for the Claim Sheet, Accessible Claim Sheet, Technical Report, and Accessible Piece. Codex reviews and owns controls/statistics, mechanism-validation analysis, and verification-dashboard rendering once the data layer exists.
- Commit messages should follow `Codex Session <#>`.
