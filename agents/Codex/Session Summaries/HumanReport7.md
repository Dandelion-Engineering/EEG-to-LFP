# Codex Session 7 Report

**Current Date and Time:** 2026-06-11 13:39 PDT

## Summary

This session picked up from Claude Session 6's active `Riemannian Ladder Verdict` handoff. Claude had already climbed the linear-to-Riemannian model ladder and found no improvement over the first logistic rung: the best new rung, `tangent_cov_all`, had mean LOSO balanced accuracy around `0.558` and still failed against the behavioral-only control. Claude also ran the MTL coverage gate and found adequate MTL coverage for all `9/9` subjects, which unblocks the mechanism layer.

Codex's useful task was therefore the behavioral-control ablation Claude requested: identify whether the strong behavioral-only control was driven by response time, correctness/match, previous-trial state, or trial/session structure.

## Work Completed

I added a reusable ablation script:

- `scripts/run_behavioral_control_ablation.py`
  - Uses the same bundle-aligned metadata and leave-one-subject-out discipline as the main control harness.
  - Reuses the same tabular preprocessing and inner subject-grouped `C` selection logic from `scripts/run_control_models.py`.
  - Hard-fails if any target-encoding forbidden column enters an ablation.
  - Emits per-subject scores, per-trial predictions/scores, JSON summary, and a compact markdown report.

I ran it against the current feature bundle:

```text
.\venv\Scripts\python.exe -m py_compile scripts\run_behavioral_control_ablation.py

.\venv\Scripts\python.exe scripts\run_behavioral_control_ablation.py --bundle outputs\features\feature_bundle.npz --metadata outputs\features\feature_metadata.csv --out-dir outputs\controls
```

Generated but ignored by git:

- `outputs/controls/behavioral_ablation_subject_scores.csv`
- `outputs/controls/behavioral_ablation_predictions.csv`
- `outputs/controls/behavioral_ablation_summary.json`
- `outputs/controls/behavioral_ablation_summary.md`

## Behavioral-Control Ablation Result

The result is decisive: the behavioral-only control is almost entirely carried by `previous_trial_correct`.

Mean LOSO balanced accuracy by component:

```text
rt_only              0.500
correct_match        0.500
previous_trial       0.596
trial_index_only     0.500
session_only         0.500
trial_order_session  0.500
full_behavioral      0.593
```

Per subject, `previous_trial_correct` was the best ablation for all `9/9` held-out subjects. It reproduces or slightly exceeds the full behavioral control in every subject.

The target-rate audit explains why:

```text
previous_trial_correct = 0.0: 130 trials, current high-load rate 0.015
previous_trial_correct = 1.0: 1523 trials, current high-load rate 0.670
previous_trial_correct = missing: 30 trials, current high-load rate 0.800
```

This matches the task rule in the dataset paper: an incorrect response is followed by a set-size-4 trial. The behavioral control is therefore not driven by response-time leakage, performance leakage, or session/trial-order drift. It is a real task-schedule channel that was allowed by the predeclared behavioral-control definition.

## Collaboration Update

I appended a Codex Session 7 response to:

- `chats/Claude-Codex/Riemannian Ladder Verdict/Riemannian Ladder Verdict - Active.md`

The reply accepts Claude's proposed split:

- Claude should run one bounded EEGNet rung, since it was predeclared and will complete the model ladder.
- Claude should start the mechanism coupling scaffold now that the MTL coverage gate is `9/9`.
- Codex treats the behavioral-control question as answered for now.
- No Claim Sheet amendment should be drafted until EEGNet and first mechanism evidence are both on the table.

## Decisions and Reasoning

The strongest control remains valid for the current Claim Sheet bar. `previous_trial_correct` was explicitly allowed in the behavioral-only control list, and the ablation shows that it exposes task structure rather than an accidental implementation leak. That means the current decoding result remains negative as scoped: the scalp decoder must beat this strongest allowed non-signal control, and neither the logistic rung nor the Riemannian rung does.

I do not recommend amending the Claim Sheet yet. If EEGNet also fails, the amendment question becomes real, but it should be framed with the mechanism evidence available. The likely amendment territory would be moving the center of gravity from "scalp decoder beats behavioral baseline" toward "scalp working-memory-load signatures are intracranially validated by MTL coupling." That is not a proposal yet; it is the decision point to revisit after the next Claude outputs.

## Challenges

The project PDF in `Project Details/` could not be cleanly extracted with local tools. MiKTeX `pdftotext` failed due a local MiKTeX configuration error, and no PDF parser library was installed in the project virtual environment. A fallback standard-library PDF stream extraction recovered enough text to verify the relevant task rule, but it was noisy and not suitable as a complete paper extraction. This did not block the ablation because the task rule was also visible in the recovered text and already reflected in prior project context.

The automation memory from the previous run was stale relative to the current repository state. I treated repository files, chat summaries, and current git history as authoritative.

## Files Created or Updated

Created:

- `scripts/run_behavioral_control_ablation.py`
- `agents/Codex/Session Summaries/HumanReport7.md`

Updated:

- `chats/Claude-Codex/Riemannian Ladder Verdict/Riemannian Ladder Verdict - Active.md`
- `agents/Codex/README.md`
- `agents/Codex/Summary of Only Necessary Context.md`

## Validation

Successful validation:

```text
.\venv\Scripts\python.exe -m py_compile scripts\run_behavioral_control_ablation.py
.\venv\Scripts\python.exe scripts\run_behavioral_control_ablation.py --bundle outputs\features\feature_bundle.npz --metadata outputs\features\feature_metadata.csv --out-dir outputs\controls
```

The rerun produced stable ablation numbers and wrote the expected ignored output artifacts.

## Git Closeout Status

The session changes could not be staged, committed, or pushed because `git add` failed:

```text
fatal: Unable to create '.../.git/index.lock': Permission denied
```

There was no project-work issue in the changed files. The blocker is repository metadata write access, matching the same `.git/index.lock` permission failure Codex saw in Session 6. The working tree contains the Session 7 changes but they remain uncommitted.

## Next Steps

Next Codex session should first read the active `Riemannian Ladder Verdict` chat. If Claude has produced EEGNet outputs, Codex should run the standard controls/statistics path on that rung before interpretation. If Claude has produced first mechanism coupling summaries, Codex should review or extend the mechanism validation and decide whether the verification dashboard needs a mechanism panel update.

Codex Session 8 should also write the every-eighth-session progress report after normal session work, unless the session is blocked before meaningful project work can occur.
