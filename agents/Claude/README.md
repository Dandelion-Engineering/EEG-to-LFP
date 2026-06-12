# Claude — Workspace

This is Claude's personal workspace for the Dandelion "EEG → deep/MTL activity" project (the first standalone rung toward the long-term "electrical fMRI" goal: reconstructing deep-brain activity from cheap scalp EEG + AI, validated against the simultaneous scalp/iEEG/MTL-unit dataset on `D:\Simultaneous EEG_LFP`).

## Folder tree

```
agents/Claude/
├── README.md                          ← this file: how to navigate my workspace
├── Summary of Only Necessary Context.md  ← AUTHORITATIVE continuity handoff; rewritten every session
├── Literature Foundation.md           ← Phase 0 deliverable: my survey of the field (6 sections)
├── references.md                      ← AUTHORITATIVE running bibliography; verified links/DOIs
├── Session Summaries/                 ← human-readable per-session reports
│   ├── HumanReport1.md
│   ├── HumanReport2.md
│   ├── HumanReport3.md
│   ├── HumanReport4.md
│   ├── HumanReport5.md
│   ├── HumanReport6.md
│   ├── HumanReport7.md
│   ├── HumanReport8.md
│   ├── HumanReport9.md
│   └── HumanReport10.md
└── Progress Reports/                  ← director-facing reports every 8th session + at phase/amendment events
    ├── Progress Report Phase 0 Close.md
    ├── Progress Report Phase 1 Close.md
    ├── Progress Report Session 8.md
    └── Progress Report Amendment 1 Decoding-to-Coupling Repoint.md
```

## What each file is for

- **Summary of Only Necessary Context.md** — The single file I re-read first each session to restore where the work stands. Authoritative for "current state." Completely rewritten at the end of every session.
- **Literature Foundation.md** — My independent Phase 0 literature survey. Stable once Phase 0 closes; informs the Claim Sheet. Not overwritten — it's a recorded turn.
- **references.md** — Every source that informed my work, with a verified link/DOI and a note on how it shaped the project. Authoritative; appended to as the project grows. Reconciled with Codex's references into the Technical Report bibliography at Phase 2.
- **Session Summaries/** — One human-readable report per session (`HumanReport<N>.md`), written for the director. Authoritative record of session history.
- **Progress Reports/** — Separate from session summaries. Director-facing deep-dives written every 8th of my sessions and at phase transitions / approved amendments. Contains `Progress Report Phase 0 Close.md` (Phase 0 → Phase 1, Session 2), `Progress Report Phase 1 Close.md` (Phase 1 → Phase 2, Session 3), `Progress Report Session 8.md` (**my first cadence report — Session 8**, covering the whole Phase 2 decoding-ladder arc), and `Progress Report Amendment 1 Decoding-to-Coupling Repoint.md` (the Amendment 1 trigger report). Next cadence report due at my Session 16; plus any future phase transition / approved amendment.

## Authoritative vs. scratch

All current files are authoritative. There is no scratch/temp content yet. If I add scratch work later, it will live in a clearly labeled `scratch/` subfolder.

## Files I own or co-own outside this folder

- `utils/` (project root) — **data + feature + model layer.** `nix_io.py` (NIX session reader: aligned scalp epochs, trial metadata, lazy iEEG/electrode access; Codex added `load_ieeg_epochs` S8), `epoching.py` (maintenance-window extraction), `features.py` (**Session 5** — band-power + tangent-space covariance feature extraction), `riemann.py` (**Session 6** — affine-invariant SPD geometry; dependency-free), `eegnet.py` (**Session 7** — dependency-free NumPy EEGNet for rung 4: conv/BatchNorm/ELU/pool/dropout/Adam + finite-difference gradient check). `mechanism.py` is Codex's (S8, co-owned). Shared modules imported by all scripts per Standards.
- `scripts/` (project root) — **Phase 2 scripts.** Data layer (Session 4): `validate_nix_reader.py`, `build_trial_metadata.py`, `audit_trial_counts.py`. Feature/decoding layer (**Session 5**): `build_features.py`, `make_loso_splits.py`, `run_load_decoder.py` (rung-1 logistic/LDA). Riemannian + mechanism layer (**Session 6**): `run_riemann_decoder.py` (rung-2 tangent + rung-3 MDM), `audit_mtl_coverage.py`. EEGNet layer (**Session 7**, **RUN Session 8**): `run_eegnet_decoder.py` (rung-4 EEGNet LOSO decoder, same output contract; gradient-checked + executed S8 once disk was freed — mean LOSO BA 0.616, headline bar NOT met). Codex's mechanism scripts (S8, co-owned): `run_behavioral_control_ablation.py`, `run_mtl_bandpower_probe.py`.
- `requirements.txt` (project root) — pinned, commercial-OK dependencies (Session 4).
- `outputs/` (project root, **gitignored / local-only**, rebuildable) — data-layer tables (`trial_metadata.*`, `session_summary.csv`, `scalp_montage.json`, `trial_count_audit.*`, `montage_intersection.json`); `outputs/features/` (Session 5: `feature_bundle.npz`, `feature_metadata.*`, `exclusions.csv`, `feature_names.json`, `loso_folds.json`, `loso_fold_assignment.csv`); `outputs/decoding/` (Session 5 rung-1 + Session 6 Riemannian rungs: `predictions_*`, `subject_scores_*`, `summary_*.json`); `outputs/mechanism/` (Session 6: `mtl_coverage.csv`, `mtl_contacts.csv`, `mtl_coverage_summary.json`).
- `deliverables/technical_report/` (project root) — **Phase 3, Technical Report deliverable (started Session 9).** `main.tex` (complete compiling LaTeX draft built around the Amendment-1 two-part result; pdflatex+bibtex, 10 pp; §5.2 confirmatory result added by Codex S11), `references.bib` (load-bearing citations from both agents' reference files; **[P3] joint reconciliation done S10**), `README.md` (build steps + remaining open item [P1] dashboard figures; [P2] and [P3] now complete). DRAFT pending Codex final approval. Build artifacts (`*.pdf`/`*.aux`/`*.log`/`*.bbl`) are gitignored and rebuilt from source.
- `deliverables/accessible_piece/` (project root) — **Phase 3, Accessible Piece deliverable (written Session 10).** `Accessible Piece.md` — full plain-language companion to the Technical Report, written for a zero-background reader, with credible-source links for every non-obvious term. Pending Codex review/approval (handed off in the *Accessible Piece Review* chat).
- `chats/Claude-Codex/...` — I co-own chat threads with Codex (*Phase 0 Literature Alignment* — concluded; *Claim Sheet Phase 1* — concluded; *Phase 2 Controls Interface* — concluded Session 5; *Riemannian Ladder Verdict* — opened S6, CONCLUDED Session 9 with `Summary.md`; *Accessible Piece Review* — **opened S10, ACTIVE**, awaiting Codex's review of the Accessible Piece + [P3] confirmation). Also `chats/Claude-Codex-Human/Some Updates` — Randy's S8 updates, concluded by Codex (bundled into my S9 push).
- `Claim Sheet.md` (project root) — I am the default writer; agent-approved rev. 2 (Phase 1, S3); **director-approved as-is S8; AMENDMENT 1 ratified S8, final wording approved by Codex S10** (decoding→coupling re-point; see Amendment log).
- `Accessible Claim Sheet.md` (project root) — my default-writer companion; written S3, **Amendment 1 synced S8**. Kept in sync with the technical sheet via the amendment protocol.
- `director_requests.md` (project root) — co-owned operational log; I opened it Session 3 with the *Claim Sheet ready for director review* entry.
- Per the framework's default writer convention, I am the **default writer** for the project's four narrative deliverables — the Claim Sheet ✓, the Accessible Claim Sheet ✓, the Technical Report (**draft S9, [P2]/[P3] closed, only [P1] figures left**), and the Accessible Piece (**written S10**, pending Codex approval). Codex reviews and approves each. Remaining unbuilt required artifact: the **Reproducibility Packet** (co-owned).

## How to navigate without prior context

Start with **Summary of Only Necessary Context.md** for the current state, then **Literature Foundation.md** for the grounding, then the latest file in **Session Summaries/** for the most recent narrative. The shared project framework lives in `/Project Details/` and `AgentPrompt.md` at the project root.
