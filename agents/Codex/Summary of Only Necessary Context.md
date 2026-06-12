# Summary of Only Necessary Context - Codex

**Last rewritten:** 2026-06-12 12:09 PDT (Codex Session 12)
**Current phase:** Phase 3 deliverable support after Amendment 1; Phase 2 evidence is concludable

Re-read `AgentPrompt.md`, `Project Details/Project Details.md`, the dataset paper in `Project Details/`, the Claim Sheet pair, and Codex-related chat summaries at the start of the next session. This file records Codex-specific continuity not already contained there.

## Current Project State

Phase 0 and Phase 1 are closed. Randy approved the original Claim Sheet pair in the concluded `chats/Claude-Codex-Human/Some Updates/` thread with no director amendments.

Amendment 1 is ratified in both `Claim Sheet.md` and `Accessible Claim Sheet.md`. It records the completed model ladder as a bounded negative and the EEGNet-to-MTL coupling as an exploratory/inconclusive mechanism lead. The original Slot 11 decoding success bar was not weakened.

All Codex-including chats are concluded at this closeout. The newest concluded chat is:

- `chats/Claude-Codex/Accessible Piece Review/Accessible Piece Review - Concluded.md`
- `chats/Claude-Codex/Accessible Piece Review/Summary.md`

Claude drafted the Technical Report under `deliverables/technical_report/`. Codex Session 11 inserted the failed Part B confirmatory coupling gate result into Section 5.2. Codex Session 12 approved the bibliography reconciliation `[P3]`, added dashboard-derived 300-DPI figures for `[P1]`, inserted them into `main.tex`, and approved the Accessible Piece after one precision edit. The report README now lists no report-local open items; the broader Phase 3 blocker is the Reproducibility Packet.

## Locked Original Headline Configuration

The original locked Phase 2 headline configuration remains important because it defines the clean negative result:

- primary target: binary high-vs-low load, set size 4 vs set sizes 6/8;
- headline epoch: maintenance period `[-3, 0]` seconds relative to probe;
- headline split: leave-one-subject-out;
- headline scalp montage: the 8 common physical channels `A1`, `A2`, `C3`, `C4`, `F3`, `F4`, `O1`, `O2`;
- no missing-channel padding, imputation, or subject-specific expanded feature spaces for the headline;
- success bar: mean LOSO balanced-accuracy improvement over strongest non-signal control at least `+0.075`, at least `7/9` held-out subjects above control, and no leave-one-subject-removed mean below `0.04`;
- evidence is subject-level; window-level permutation cannot substitute.

Do not run additional headline decoders to rescue this original bar. Frequency-domain CNNs, richer channel sets, or within-subject runs would be diagnostics/new claims, not a rescue of the locked common-montage LOSO headline.

## Completed Decoding Results

The pre-registered model ladder is exhausted:

- `logistic_all_all`: mean signal BA `0.560`; strongest-control BA `0.593`; improvement `-0.033`; `3/9` subjects above control; headline success `no`.
- `tangent_cov_all`: mean signal BA `0.558`; strongest-control BA `0.593`; improvement `-0.036`; `3/9` subjects above control; headline success `no`.
- `eegnet_raw_all`: mean signal BA `0.616`; strongest-control BA `0.593`; improvement `+0.023`; `5/9` subjects above control; min leave-one-subject-removed mean `-0.001`; bootstrap 95% CI `[-0.022, 0.081]`; headline success `no`.

EEGNet was the first rung to beat behavioral control on the mean, but it fails the declared bar and is S04-driven:

```text
S01 improvement  +0.045
S02 improvement  -0.055
S03 improvement  -0.015
S04 improvement  +0.218
S05 improvement  -0.067
S06 improvement  +0.045
S07 improvement  -0.015
S08 improvement  +0.009
S09 improvement  +0.044
```

Removing S04 drops mean improvement to `-0.001`. Treat this as the clean negative boundary the robustness rule was designed to catch.

The brain-only EEGNet diagnostic remains: mean LOSO BA `0.623` on the 6 brain channels vs `0.616` on all 8 channels. This passes the A1/A2 reference sensitivity check for rung 4 and does not change the headline failure.

## Behavioral-Control State

The strongest non-signal control remains behavioral-only for all subjects. Codex Session 7 showed that it is almost entirely `previous_trial_correct`, reflecting the task rule that an incorrect response is followed by a set-size-4 trial:

```text
previous_trial_correct = 0.0: current high-load rate 0.015
previous_trial_correct = 1.0: current high-load rate 0.670
previous_trial_correct = missing: current high-load rate 0.800
```

This is not response-time leakage, correctness/match leakage, or session/trial-order drift. It was predeclared as an allowed behavioral covariate, so it remains the valid strongest control under the current Claim Sheet.

## Mechanism State

MTL coverage is adequate for all `9/9` subjects. Coverage alone does not support the deep-readout claim.

The MTL band-power probe against `tangent_cov_all` found a real-looking intracranial substrate but no coupling to tangent scores:

```text
MTL theta-alpha load effect z: mean 0.143, 7/9 positive, p2=0.0156
corr(tangent score, theta-alpha): mean -0.015, 5/9 positive, p2=0.8086
```

The MTL band-power probe against EEGNet scores found the same substrate and a suggestive raw coupling:

```text
MTL theta-alpha load effect z: mean 0.143, 7/9 positive, p2=0.0156
corr(EEGNet score, MTL theta): mean 0.078, 6/9 positive, p2=0.1641
corr(EEGNet score, MTL alpha): mean 0.057, 6/9 positive, p2=0.2852
corr(EEGNet score, theta-alpha): mean 0.068, 7/9 positive, p2=0.0508
```

Codex Session 9 residualized the fixed EEGNet score vs MTL theta-alpha relationship:

```text
raw score-MTL theta-alpha diff:       mean 0.068, 7/9 positive, p2=0.0508
load-residualized:                    mean 0.050, 5/9 positive, p2=0.1328
schedule-residualized:                mean 0.011, 4/9 positive, p2=0.7461
behavior-residualized:                mean 0.013, 5/9 positive, p2=0.7148
```

Codex Session 11 added and ran `scripts/run_mtl_confirmatory_coupling_gate.py` as the prospective Part B gate. Gate criteria:

- fixed metric: `corr_schedule_residual_score_mtl_theta_alpha_diff`;
- mean correlation must be positive;
- at least `7/9` subjects positive;
- exact two-sided subject sign-flip `p <= 0.05`;
- every leave-one-subject-out mean must be above `0`.

Result:

```text
gate_passed = False
schedule-residualized mean = 0.011
positive subjects = 4/9
p2 = 0.7461
min leave-one-subject-out mean = -0.010
```

Interpretation: Part B remains exploratory/inconclusive. Do not describe the raw coupling as validated deep-source-related information.

## Session 12 Deliverable Updates

Codex Session 12 changed:

- `deliverables/accessible_piece/Accessible Piece.md` - approved with one precision edit: simpler models fell short of the strong shortcut; EEGNet was the only rung above strongest control on the mean.
- `scripts/export_dashboard_report_figures.py` - new Codex-owned exporter from final dashboard inputs to tracked 300-DPI report PNGs.
- `deliverables/technical_report/figures/eegnet_raw_all_subject_improvements.png` - per-subject EEGNet improvement figure showing S04 dependence and unmet +0.075 bar.
- `deliverables/technical_report/figures/eegnet_raw_all_mtl_coupling_residualization.png` - mechanism sensitivity figure showing raw-to-residualized coupling collapse and failed confirmatory gate.
- `deliverables/technical_report/main.tex` - inserted both figures and updated report status comments.
- `deliverables/technical_report/README.md` - marks report-side `[P1]` and `[P3]` complete; no report-local open items remain.
- `deliverables/technical_report/references.bib` - header records Codex approval of bibliography reconciliation.
- `chats/Claude-Codex/Accessible Piece Review/Accessible Piece Review - Concluded.md` and `Summary.md` - chat concluded after approval/handoff.
- `agents/Codex/README.md` - refreshed for Session 12, new exporter, approved Accessible Piece, and concluded chat state.
- `agents/Codex/Session Summaries/HumanReport12.md` - Session 12 report.
- `agents/Codex/Summary of Only Necessary Context.md` - this file.

Final report-figure export command:

```text
.\venv\Scripts\python.exe scripts\export_dashboard_report_figures.py --subject-statistics outputs\statistics\subject_statistics_eegnet_raw_all.csv --summary outputs\statistics\summary_eegnet_raw_all.json --mechanism-gate outputs\mechanism\mtl_confirmatory_coupling_gate_eegnet_raw_all.json --mechanism-subject-summary outputs\mechanism\mtl_residual_coupling_subject_summary_eegnet_raw_all.csv --out-dir deliverables\technical_report\figures --dpi 300
```

## Verification State

Python verification passed:

```text
.\venv\Scripts\python.exe -m py_compile scripts\export_dashboard_report_figures.py scripts\render_verification_dashboard.py
```

A direct citation/figure-path check passed: no missing `\cite{}` keys and no missing `\includegraphics{}` paths.

Local image inspection found both new PNGs readable and correctly framed.

LaTeX verification is still blocked before the report source is read. `pdflatex -interaction=nonstopmode main.tex` from `deliverables/technical_report/` fails because MiKTeX cannot rebuild `pdflatex.fmt`: `formats.ini` is missing and MiKTeX reports a local lock-path permission failure. Treat this as a local TeX installation issue to fix before final PDF verification.

## Git Closeout State

Codex Session 12 attempted the required stage/commit/push after all closeout files were written. The attempt failed before staging because Git could not create `.git/index.lock`:

```text
fatal: Unable to create '.../.git/index.lock': Permission denied
```

`Test-Path .git\index.lock` returned `False`, so this is not a stale lock file. The Session 12 files are updated in the working tree but remain uncommitted and unpushed. A future run with Git metadata write access should stage these files and commit `Codex Session 12` before adding more work if possible, or Claude/Randy may include the completed Codex session work in a later combined commit under the agreed protocol.

## Remaining Phase 3 Work

The next major blocker is the Reproducibility Packet:

1. Create the packet structure and README that walks an outside reader from public dataset download through final outputs.
2. Include or reference the verification dashboard as the reader's first way into the result.
3. Add packet-local `.gitignore` and license files consistent with dataset CC BY-SA handling and Dandelion code licensing.
4. Confirm the packet's command sequence reproduces the final EEGNet controls/statistics/dashboard/figures from a fresh environment given the dataset path.
5. Re-test PDF generation after MiKTeX is repaired or replaced.

## Hard Guards To Preserve

- Held-out subject is scored once; all model/feature/window choices happen inside training subjects only.
- Adjacent windows from the same trial cannot straddle train/test boundaries.
- Behavioral-only control must exclude set size, `load_binary`, and every set-size-encoding variable.
- Timing-only control must not include response time, correctness, match/mismatch, neural features, or target encodings.
- A1/A2 are ear/mastoid references; brain-only diagnostics are required but cannot move the headline bar after results are observed.
- Mechanism full-claim support requires adequate MTL coverage and actual coupling evidence, not coverage alone.
- Raw EEGNet-to-MTL coupling `p2=0.0508` is exploratory because the residualized confirmatory gate failed.
- No raw dataset files, large binaries, generated ignored outputs, scratch probes, local lock files, or local venv files should be committed.

## Local Substrate Facts

- Dataset path: `D:\Simultaneous EEG_LFP`.
- Project virtual environment exists at `.\venv`; always use `.\venv\Scripts\python.exe` and `.\venv\Scripts\pip.exe`.
- Common maintenance timing is fixed across trials: fixation `-6 s`, encoding `-5 s`, maintenance `-3 s`, probe `0 s`.
- iEEG data arrays are trial-aligned, typically shaped `(n_contacts, 16000)`, sampled at `2000 Hz`, and offset `-6 s` relative to probe.
