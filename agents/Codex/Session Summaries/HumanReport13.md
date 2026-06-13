# Codex Human Report 13

**Current Date and Time:** 2026-06-12 14:45 PDT

## Summary

This session followed the project lock protocol. No `.codex-session.lock` was present at start, so Codex created it before reading `AgentPrompt.md`, the Project Details, the dataset paper text available through local extraction, Codex's restart summary, the Claim Sheet pair, and all Codex-including chat summaries/active chats.

The active work item was Claude's new `Reproducibility Packet Review` chat. Claude had built `deliverables/reproducibility_packet/` and asked Codex to review the packet, sanity-check the decision not to duplicate `scripts/` and `utils/`, and explicitly approve the Technical Report source.

## What was accomplished

First, Codex reviewed the Reproducibility Packet structure and approved its direction. The packet correctly treats the repository as the reproduction unit: the packet README is the external reader's walkthrough, while the source code remains in the root `scripts/` and `utils/` modules. I agreed with this choice because duplicating the code into the packet would create a stale fork and conflict with the project standard against copy-pasted shared logic.

Second, Codex ran packet validation checks. The script CLI surface is valid: every packet-listed script returned usable `--help` under the pinned project virtual environment. The installed venv versions match both the root and packet `requirements.txt` pins. The shipped verification dashboard is self-contained: no external URL/fetch dependency was found. The cheap packet reproduction checks passed: `scripts/summarize_subject_statistics.py` reproduced the headline EEGNet gate numbers (`+0.023`, `5/9`, min leave-one-out `-0.001`, headline success `no`); `scripts/run_mtl_confirmatory_coupling_gate.py` reproduced `gate_passed=false`, schedule-residualized mean `+0.011`, `4/9`, `p2=0.7461`; and `scripts/render_verification_dashboard.py` regenerated an HTML file byte-identical to `deliverables/reproducibility_packet/verification_dashboard.html`.

Third, Codex started a clean-output validation pass in an ignored scratch tree rather than relying only on the existing `outputs/` cache. That pass succeeded through the reader validation, trial metadata build, montage audit, feature build, LOSO split generation, logistic decoder, tangent-space Riemannian decoder, and MDM decoder. It reproduced the expected 37 NIX files, 1,827 trial rows, 1,683 retained trials, 144 dropped artifact trials, the locked 8-channel common montage (`A1`, `A2`, `C3`, `C4`, `F3`, `F4`, `O1`, `O2`), and expected non-CNN mean LOSO balanced accuracies: logistic `0.560`, tangent `0.558`, and MDM `0.533`.

Fourth, Codex attempted the slow clean-output EEGNet headline run. That foreground run exceeded a one-hour timeout before producing `predictions_eegnet_raw_all.csv`, so I did not stamp the packet fully complete. Existing canonical `outputs/` still support the packet and dashboard, but the strictest reading of the Dandelion Standards still wants either an uninterrupted default EEGNet run from a clean output tree, followed by downstream controls/statistics/mechanism/dashboard regeneration, or an explicit written decision that the already validated `outputs/` EEGNet artifacts are accepted as the canonical expensive-stage cache.

Fifth, Codex approved the Technical Report source as a deliverable source. I changed `deliverables/technical_report/main.tex` and `deliverables/technical_report/README.md` from draft status to source-approved status. I reran source-level checks: no missing `\cite{}` keys, no missing `\includegraphics{}` paths, and the report/dashboard-related scripts compile under the pinned venv.

Sixth, Codex appended a response to `chats/Claude-Codex/Reproducibility Packet Review/Reproducibility Packet Review - Active.md` documenting the report approval, packet structure approval, validation checks, the one-hour EEGNet timeout, and the remaining Phase 3 gate.

## Challenges and handling

MiKTeX remains broken locally. `pdflatex -interaction=nonstopmode main.tex` still fails before reading the report source because MiKTeX cannot rebuild `pdflatex.fmt`; it reports `formats.ini` missing and a lock-path permission failure under the local MiKTeX directory. I therefore treated PDF compilation as an environment blocker and relied on source-level validation for report approval.

The local `pdftotext` command also emits the same MiKTeX lock-path fatal messages, but it still produced readable paper text on stdout. I used it only to confirm access to the dataset paper text, not for deliverable verification.

The clean-output EEGNet run did not complete within one hour. I treated that as a real validation gap rather than a failure of the model or packet. No clean-output EEGNet files were produced in the scratch tree.

Git status showed an untracked root `outputs_cleanroom/` generated-output directory. Because this is pipeline output and should not be committed, I added `/outputs_cleanroom/` to the root `.gitignore`.

Git closeout failed before staging. `git add` returned `fatal: Unable to create '.../.git/index.lock': Permission denied`. `Test-Path .git\index.lock` returned `False`, so this is not a stale lock file. The Session 13 changes remain in the working tree uncommitted and unpushed.

## Important decisions

- Approved the Technical Report source, but not local PDF generation, because the source checks pass and the TeX failure occurs before source processing.
- Approved the Reproducibility Packet structure and content direction, including the repository-as-reproduction-unit design.
- Did not fully approve the Reproducibility Packet or close Phase 3 because the clean-output EEGNet validation gate is still unresolved.
- Left the `Reproducibility Packet Review` chat active because Claude needs to either run/coordinate the slow validation or accept the existing expensive-stage cache explicitly.

## Validation

Commands and checks run included:

```text
.\venv\Scripts\python.exe <packet-listed script> --help
.\venv\Scripts\python.exe scripts\summarize_subject_statistics.py --control-subject-scores outputs\controls\control_subject_scores_eegnet_raw_all.csv --out-dir outputs\statistics --tag eegnet_raw_all
.\venv\Scripts\python.exe scripts\run_mtl_confirmatory_coupling_gate.py --residual-summary outputs\mechanism\mtl_residual_coupling_summary_eegnet_raw_all.json --subject-summary outputs\mechanism\mtl_residual_coupling_subject_summary_eegnet_raw_all.csv --out-dir outputs\mechanism --tag eegnet_raw_all
.\venv\Scripts\python.exe scripts\render_verification_dashboard.py --predictions outputs\controls\control_predictions_eegnet_raw_all.csv --subject-statistics outputs\statistics\subject_statistics_eegnet_raw_all.csv --summary outputs\statistics\summary_eegnet_raw_all.json --mechanism-gate outputs\mechanism\mtl_confirmatory_coupling_gate_eegnet_raw_all.json --mechanism-subject-summary outputs\mechanism\mtl_residual_coupling_subject_summary_eegnet_raw_all.csv --out-dir outputs\dashboard
.\venv\Scripts\python.exe -m py_compile scripts\render_verification_dashboard.py scripts\export_dashboard_report_figures.py scripts\run_eegnet_decoder.py scripts\run_mtl_confirmatory_coupling_gate.py
```

The rendered dashboard hash matched the shipped packet dashboard exactly. Citation-key and figure-path checks passed. The clean-output validation succeeded through non-CNN model rungs and timed out at the default EEGNet rung after one hour.

## Files created or updated

- `deliverables/technical_report/main.tex` - marked source approved; removed draft macro; fixed approved date.
- `deliverables/technical_report/README.md` - marked source approved and documented the MiKTeX compile blocker.
- `chats/Claude-Codex/Reproducibility Packet Review/Reproducibility Packet Review - Active.md` - appended Codex's review response.
- `.gitignore` - added `/outputs_cleanroom/` so generated clean-output artifacts are not tracked.
- `agents/Codex/Session Summaries/HumanReport13.md` - this report.
- `agents/Codex/README.md` - refreshed navigation for Session 13.
- `agents/Codex/Summary of Only Necessary Context.md` - rewritten at closeout.

## Next steps

- Resolve the Reproducibility Packet validation gate: run the default EEGNet headline stage uninterrupted in a clean output tree, then downstream controls/statistics/mechanism/dashboard, or explicitly accept the prior validated `outputs/` EEGNet artifacts as the canonical expensive-stage cache.
- Keep `chats/Claude-Codex/Reproducibility Packet Review/` active until that decision is made and the packet is fully approved.
- After packet approval, Phase 3 can close and the closing agent should write the Phase 3 Close progress report.
- MiKTeX still needs repair before final PDF compile verification can be relied on.
- Commit/push still needs to be completed from an environment that can write `.git/index.lock`, or Claude/Randy can include the completed Session 13 files in a later combined commit under the existing protocol.
