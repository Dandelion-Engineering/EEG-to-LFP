# Codex Session 9 Report

**Current Date and Time:** 2026-06-12 08:12 PDT

## Summary

This session picked up after Randy cleared disk space and approved the Claim Sheet. I confirmed the new human-facing instructions in the `Some Updates` chat, concluded that chat, and saved its summary. The important directives from Randy are now preserved: the Claim Sheet pair is approved with no amendment, the disk-space blocker for EEGNet is resolved, and Codex should keep trying to push while reporting any failure; Claude may push completed Codex sessions alongside Claude's own completed session work.

The EEGNet evidence landed during this session. The headline EEGNet rung (`eegnet_raw_all`) reached mean LOSO balanced accuracy `0.616`, which is better than the behavioral control mean `0.593`, but it still failed all predeclared success criteria: mean improvement only `+0.023`, only `5/9` subjects above strongest control, and leave-one-subject-removed mean improvement collapsed to `-0.001` when S04 was removed. The decoding half is therefore exhausted across the pre-registered ladder and remains a clean negative under the current Claim Sheet.

I then added a residualized mechanism sensitivity script because the raw EEGNet-to-MTL coupling result was suggestive but too easy to overstate. The new script tests whether the fixed EEGNet score vs MTL theta-alpha differential relationship survives load, task-schedule, and behavioral residualization. It does not: the raw coupling is `0.068`, `7/9`, p2 `0.0508`, but after schedule residualization it drops to mean `0.011`, `4/9`, p2 `0.7461`. This changes the amendment recommendation: re-pointing is warranted, but the mechanism half should be framed as exploratory/inconclusive rather than validated.

## Work Completed

Created:

- `scripts/run_mtl_residual_coupling_probe.py`
  - Consumes `outputs/mechanism/mtl_bandpower_trial_summary_<tag>.csv` and `outputs/features/feature_metadata.csv`.
  - Computes the fixed subject-level correlation between EEGNet `signal_score` and `mtl_theta_alpha_log_power_diff`.
  - Recomputes that relationship after residualizing both variables within subject against load, load plus task schedule, and load plus schedule plus behavioral covariates.
  - Writes CSV, JSON, and Markdown summaries.

Generated ignored outputs:

- `outputs/mechanism/mtl_residual_coupling_subject_summary_eegnet_raw_all.csv`
- `outputs/mechanism/mtl_residual_coupling_summary_eegnet_raw_all.json`
- `outputs/mechanism/mtl_residual_coupling_summary_eegnet_raw_all.md`

Updated:

- `chats/Claude-Codex-Human/Some Updates/Some Updates - Concluded.md`
  - Appended Codex's confirmation of Randy's disk-space, Claim Sheet, and git-protocol instructions.
- `chats/Claude-Codex-Human/Some Updates/Summary.md`
  - Summarized the concluded Randy/Claude/Codex update thread.
- `chats/Claude-Codex/Riemannian Ladder Verdict/Riemannian Ladder Verdict - Active.md`
  - Responded to Claude's post-EEGNet amendment proposal.
  - Agreed that the decoding ladder is exhausted and no more headline decoder should be run.
  - Pushed back on mechanism wording: the result is suggestive and control-sensitive, not validated.
- `agents/Codex/README.md`
  - Added HumanReport9, the concluded `Some Updates` chat, and the residual-coupling probe to the navigation list.

Verified existing EEGNet artifacts:

- `outputs/decoding/predictions_eegnet_raw_all.csv`
- `outputs/decoding/subject_scores_eegnet_raw_all.csv`
- `outputs/statistics/summary_eegnet_raw_all.md`
- `outputs/mechanism/mtl_bandpower_summary_eegnet_raw_all.md`

## Key Results

EEGNet decoding:

```text
Mean signal balanced accuracy:             0.616
Mean strongest-control balanced accuracy:  0.593
Mean improvement:                          0.023
Subjects above strongest control:          5/9
Min leave-one-subject-removed mean:       -0.001
Bootstrap 95% CI:                         [-0.022, 0.081]
Headline success:                          no
```

Residual coupling sensitivity:

```text
raw score-MTL theta-alpha diff:       mean 0.068, 7/9 positive, p2=0.0508
load-residualized:                    mean 0.050, 5/9 positive, p2=0.1328
schedule-residualized:                mean 0.011, 4/9 positive, p2=0.7461
behavior-residualized:                mean 0.013, 5/9 positive, p2=0.7148
```

Interpretation: the raw EEGNet score/MTL theta-alpha relationship is the strongest mechanism lead so far, but it cannot be used as a confirmed mechanism claim. It weakens under controls that remove the known load and task-schedule structure, especially the previous-trial-correctness pathway that already explained the behavioral control.

## Decisions and Reasoning

I agreed with Claude that the original decoding half has reached its end under the current Claim Sheet. Running another model to chase the declared +0.075 bar would be post hoc. The only honest move is to record the boundary: the 8-channel common-montage LOSO decoder does not produce a robust subject-transferable load readout above the strongest control.

I did not agree with framing the mechanism result as validated. The current p2 `0.0508` result was discovered after looking across a small family of metrics and is borderline even before correction. More importantly, the residualized check shows that the effect does not survive stricter schedule/behavior controls. The amendment should therefore center on a clean negative decoding boundary plus a suggestive deep-mechanism lead, not a positive mechanism claim.

## Validation

Successful commands:

```text
.\venv\Scripts\python.exe -m py_compile scripts\run_mtl_residual_coupling_probe.py
.\venv\Scripts\python.exe scripts\run_mtl_residual_coupling_probe.py --trial-summary outputs\mechanism\mtl_bandpower_trial_summary_eegnet_raw_all.csv --metadata outputs\features\feature_metadata.csv --out-dir outputs\mechanism
```

The default EEGNet run exceeded the shell tool's two-hour timeout in this Codex session, but complete EEGNet output files existed afterward and Claude Session 8 posted the full controls/statistics/MTL sequence. I verified those summary artifacts directly before responding in chat.

## Git Closeout Status

I attempted a narrow `git add` for Codex-owned closeout files plus the shared coordination files required for this session:

```text
agents/Codex/README.md
agents/Codex/Summary of Only Necessary Context.md
agents/Codex/Session Summaries/HumanReport9.md
scripts/run_mtl_residual_coupling_probe.py
chats/Claude-Codex-Human/Some Updates/Some Updates - Concluded.md
chats/Claude-Codex-Human/Some Updates/Summary.md
chats/Claude-Codex/Riemannian Ladder Verdict/Riemannian Ladder Verdict - Active.md
director_requests.md
```

It failed before staging:

```text
fatal: Unable to create '.../.git/index.lock': Permission denied
```

`Test-Path .git\index.lock` returned `False`, so this is not a stale lock file. It is the same git metadata permission failure seen in earlier Codex sessions. No commit or push was possible.

Claude-owned concurrent files remained unstaged and were not modified by Codex:

```text
agents/Claude/README.md
agents/Claude/Summary of Only Necessary Context.md
agents/Claude/references.md
agents/Claude/Progress Reports/Progress Report Session 8.md
agents/Claude/Session Summaries/HumanReport8.md
```

## Next Steps

1. Claude should draft the Claim Sheet amendment and synced Accessible Claim Sheet using narrowed language: clean negative decoding boundary plus exploratory/inconclusive MTL coupling lead.
2. Codex should review that amendment, with special attention to not turning the raw p2 `0.0508` probe into a confirmed mechanism success.
3. Any future mechanism-success bar should include a residualization or robustness requirement, not only raw score-to-MTL correlation.
4. The brain-only EEGNet reference diagnostic can still be reported when available, but it does not change the headline failure.
