# Summary of Only Necessary Context - Codex

**Last rewritten:** 2026-06-12 09:10 PDT (Codex Session 10)
**Current phase:** Phase 2 has a concludable amended result; Phase 3 deliverables likely next but not formally opened

Re-read `AgentPrompt.md`, `Project Details/Project Details.md`, the dataset paper in `Project Details/`, the Claim Sheet pair, and Codex-related chat summaries at the start of the next session. This file records Codex-specific continuity not already contained there.

## Current Project State

Phase 0 and Phase 1 are closed. Randy approved the original Claim Sheet pair in the concluded `chats/Claude-Codex-Human/Some Updates/` thread with no director amendments.

Claude Session 8 drafted Amendment 1 into both `Claim Sheet.md` and `Accessible Claim Sheet.md` while Codex Session 10 was closing out. Codex Session 10 reviewed and approved the final wording in the active `Riemannian Ladder Verdict` chat. Amendment 1 records the completed model ladder as a bounded negative and the EEGNet-to-MTL coupling as an exploratory/inconclusive mechanism lead. The original slots remain preserved; the current direction is the original contract as modified by Amendment 1.

The active coordination thread remains:

- `chats/Claude-Codex/Riemannian Ladder Verdict/Riemannian Ladder Verdict - Active.md`

Claude's amendment files were still uncommitted at Session 10 closeout and `.claude-session.lock` was still present, so Codex did not rename/conclude the chat or stage Claude-owned files. The chat objective is otherwise ready to conclude and summarize.

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

The brain-only EEGNet diagnostic landed in Claude's amendment message: mean LOSO BA `0.623` on the 6 brain channels vs `0.616` on all 8 channels. This passes the A1/A2 reference sensitivity check for rung 4 and does not change the headline failure.

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

Codex Session 8 added:

- `utils.nix_io.load_ieeg_epochs(...)`
- `utils/mechanism.py`
- `scripts/run_mtl_bandpower_probe.py`

The MTL band-power probe against `tangent_cov_all` found a real-looking intracranial substrate but no coupling to tangent scores:

```text
MTL theta-alpha load effect z: mean 0.143, 7/9 positive, p2=0.0156
corr(tangent score, theta-alpha): mean -0.015, 5/9 positive, p2=0.8086
```

Claude Session 8 reran the probe against EEGNet scores. The MTL substrate remained the same and raw score-to-MTL coupling became suggestive:

```text
MTL theta-alpha load effect z: mean 0.143, 7/9 positive, p2=0.0156
corr(EEGNet score, MTL theta): mean 0.078, 6/9 positive, p2=0.1641
corr(EEGNet score, MTL alpha): mean 0.057, 6/9 positive, p2=0.2852
corr(EEGNet score, theta-alpha): mean 0.068, 7/9 positive, p2=0.0508
```

Codex Session 9 added `scripts/run_mtl_residual_coupling_probe.py` to test whether the fixed EEGNet score vs MTL theta-alpha relationship survives load/schedule/behavior residualization. Command:

```text
.\venv\Scripts\python.exe scripts\run_mtl_residual_coupling_probe.py --trial-summary outputs\mechanism\mtl_bandpower_trial_summary_eegnet_raw_all.csv --metadata outputs\features\feature_metadata.csv --out-dir outputs\mechanism
```

Residual-coupling result:

```text
raw score-MTL theta-alpha diff:       mean 0.068, 7/9 positive, p2=0.0508
load-residualized:                    mean 0.050, 5/9 positive, p2=0.1328
schedule-residualized:                mean 0.011, 4/9 positive, p2=0.7461
behavior-residualized:                mean 0.013, 5/9 positive, p2=0.7148
```

Interpretation: the raw EEGNet-to-MTL coupling is the first positive mechanism lead, but it is exploratory and control-sensitive. It should not be described as validated deep-source-related information. It weakens after removing the load/task-schedule pathway that also explains the behavioral control.

## Session 10 Amendment Evidence Packet

Codex Session 10 added:

- `scripts/summarize_phase2_amendment_evidence.py`

Command:

```text
.\venv\Scripts\python.exe scripts\summarize_phase2_amendment_evidence.py --statistics-summary outputs\statistics\summary_eegnet_raw_all.json --behavioral-ablation-summary outputs\controls\behavioral_ablation_summary.json --bandpower-summary outputs\mechanism\mtl_bandpower_summary_eegnet_raw_all.json --residual-summary outputs\mechanism\mtl_residual_coupling_summary_eegnet_raw_all.json --out-dir outputs\amendment
```

Ignored outputs:

- `outputs/amendment/phase2_amendment_evidence_eegnet_raw_all.json`
- `outputs/amendment/phase2_amendment_evidence_eegnet_raw_all.md`

This packet compiles the fixed EEGNet statistics, behavioral-control source, MTL substrate, and residual-coupling rows into one auditable artifact for the amendment discussion. It should help deliverable drafting without overstating the mechanism result. Cite the script in tracked docs; the generated `outputs/` packet is intentionally ignored and reproducible.

## Amendment 1 Review Position

Codex Session 10 approved Amendment 1 with this evidence line:

- The Slot 11 decoding success bar is not weakened.
- Part A is a bounded negative across the completed common-montage LOSO model ladder.
- Part B is exploratory/inconclusive, not validated deep-source readout.
- Any future mechanism-success bar must include residualization/robustness requirements or be explicitly prospective. Do not launder the already-inspected raw p2=`0.0508` into a confirmed headline by simply naming it confirmatory after the fact.

Claude wrote the amendment-trigger progress report in:

- `agents/Claude/Progress Reports/Progress Report Amendment 1 Decoding-to-Coupling Repoint.md`

## Active Chat State

Active thread:

- `chats/Claude-Codex/Riemannian Ladder Verdict/Riemannian Ladder Verdict - Active.md`

Important latest state:

- Claude Session 8 proposed a Claim Sheet amendment after EEGNet.
- Codex Session 9 agreed the decoding half is done and agreed an amendment is warranted, but pushed back on mechanism wording because the raw coupling result is suggestive/inconclusive, not validated.
- Codex Session 10 added the amendment-evidence summarizer note and command.
- Claude Session 8 drafted Amendment 1 into both Claim Sheets, adopted Codex's narrower mechanism language, reported brain-only EEGNet BA `0.623`, and wrote the amendment-trigger progress report.
- Codex Session 10 reviewed and approved the final Amendment 1 wording.
- The chat remains active because `.claude-session.lock` was still present at Session 10 closeout. The objective is otherwise ready to conclude and summarize.

Concluded human-including thread:

- `chats/Claude-Codex-Human/Some Updates/Some Updates - Concluded.md`
- `chats/Claude-Codex-Human/Some Updates/Summary.md`

That thread records Randy's Claim Sheet approval, disk-space update, and git protocol.

## Available Local Artifacts

Generated outputs remain intentionally ignored by git under `/outputs/`, but the local workspace has:

- feature bundle and metadata under `outputs/features/`;
- completed decoding outputs for logistic/LDA/Riemannian rungs under `outputs/decoding/`;
- completed EEGNet headline outputs under `outputs/decoding/predictions_eegnet_raw_all.csv`, `subject_scores_eegnet_raw_all.csv`, and `summary_eegnet_raw_all.json`;
- brain-only EEGNet diagnostic outputs under `outputs/decoding/predictions_eegnet_raw_brain.csv` and `subject_scores_eegnet_raw_brain.csv`;
- EEGNet controls under `outputs/controls/control_*_eegnet_raw_all.csv`;
- EEGNet subject statistics under `outputs/statistics/summary_eegnet_raw_all.*` and `subject_statistics_eegnet_raw_all.csv`;
- MTL band-power summaries for tangent and EEGNet under `outputs/mechanism/mtl_bandpower_*`;
- residual coupling summaries for EEGNet under `outputs/mechanism/mtl_residual_coupling_*_eegnet_raw_all.*`;
- amendment evidence packet under `outputs/amendment/phase2_amendment_evidence_eegnet_raw_all.*`.

## Git And Concurrent Work State

At Session 10 start, dirty files included Claude-owned edits, Codex Session 9 edits, shared chat edits, and untracked Session 9 files. Do not revert Claude's changes.

Claude-owned/concurrent files observed:

- `agents/Claude/README.md`
- `agents/Claude/Summary of Only Necessary Context.md`
- `agents/Claude/references.md`
- `agents/Claude/Progress Reports/Progress Report Session 8.md`
- `agents/Claude/Session Summaries/HumanReport8.md`
- `director_requests.md`
- `Claim Sheet.md`
- `Accessible Claim Sheet.md`
- `agents/Claude/Progress Reports/Progress Report Amendment 1 Decoding-to-Coupling Repoint.md`

Codex-owned or Codex-touched files from Sessions 9-10 include:

- `agents/Codex/README.md`
- `agents/Codex/Summary of Only Necessary Context.md`
- `agents/Codex/Session Summaries/HumanReport9.md`
- `agents/Codex/Session Summaries/HumanReport10.md`
- `scripts/run_mtl_residual_coupling_probe.py`
- `scripts/summarize_phase2_amendment_evidence.py`
- `chats/Claude-Codex/Riemannian Ladder Verdict/Riemannian Ladder Verdict - Active.md`
- `chats/Claude-Codex-Human/Some Updates/Some Updates - Concluded.md`
- `chats/Claude-Codex-Human/Some Updates/Summary.md`

Codex Sessions 9 and 10 could not stage because git failed with:

```text
fatal: Unable to create '.../.git/index.lock': Permission denied
```

`Test-Path .git\index.lock` returned `False`, so it was not a stale lock file. Session 10 attempted a narrow `git add` for completed Codex files and hit the same error before staging anything. No Codex commit or push was possible. Claude's Session 8 commit is already on `origin/main` and includes the Claim Sheet amendment and active chat; the pending Codex files remain in the working tree for a future Claude/Randy push or a Codex session with working git metadata writes.

## Hard Guards To Preserve

- Held-out subject is scored once; all model/feature/window choices happen inside training subjects only.
- Adjacent windows from the same trial cannot straddle train/test boundaries.
- Behavioral-only control must exclude set size, `load_binary`, and every set-size-encoding variable.
- Timing-only control must not include response time, correctness, match/mismatch, neural features, or target encodings.
- A1/A2 are ear/mastoid references; brain-only diagnostics are required but cannot move the headline bar after results are observed.
- Mechanism full-claim support requires adequate MTL coverage and actual coupling evidence, not coverage alone.
- The MTL band-power, residual-coupling, and amendment-evidence scripts are mechanism/amendment scaffolds, not full mechanism success results.
- No raw dataset files, large binaries, generated outputs, scratch probes, local lock files, or local venv files should be committed.

## Next Actions

For Codex:

1. If the amendment wording changes, review it against the narrowed evidence language above.
2. Use `scripts/summarize_phase2_amendment_evidence.py` as the compact evidence packet generator for amendment/deliverable review.
3. Keep `scripts/run_mtl_residual_coupling_probe.py` as the current Codex-owned mechanism sensitivity analysis.
4. If the prospective confirmatory coupling test runs, bake in the residualization/robustness criterion from Amendment 1.
5. Treat the brain-only EEGNet diagnostic as an artifact/reference check only; it cannot alter the headline failure.
6. If git metadata writes work, carefully stage/commit Codex-owned completed files while preserving Claude's concurrent work. Pending completed Codex files are listed in the Git section above.

## Local Substrate Facts

- Dataset path: `D:\Simultaneous EEG_LFP`.
- Project virtual environment exists at `.\venv`; always use `.\venv\Scripts\python.exe` and `.\venv\Scripts\pip.exe`.
- Common maintenance timing is fixed across trials: fixation `-6 s`, encoding `-5 s`, maintenance `-3 s`, probe `0 s`.
- iEEG data arrays are trial-aligned, typically shaped `(n_contacts, 16000)`, sampled at `2000 Hz`, and offset `-6 s` relative to probe.
