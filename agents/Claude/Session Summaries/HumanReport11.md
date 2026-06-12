# Claude Human Report 11

**Current Date and Time:** 2026-06-12 13:13 PDT

## Summary

This session built the **Reproducibility Packet** — the last of the three required Dandelion
deliverables that had not yet been written. With it assembled and validated, all three
deliverables now exist; the project is one Codex review pass away from being able to close
Phase 3.

### Context at session start

I followed the session-lock protocol: no `.claude-session.lock` was present, so I created it
before reading `AgentPrompt.md`, the full Project Details, the dataset paper folder listing, my
own `Summary of Only Necessary Context`, the Claim Sheet (including ratified Amendment 1), and
all Claude-including chat summaries and active chats.

The big change since my last session: **Codex ran Session 12** and closed out the items I had
handed him in the *Accessible Piece Review* chat. He **approved the Accessible Piece** (with one
precision edit I agree with — see Cross-review), **confirmed the bibliography reconciliation
[P3]**, and **closed the Technical Report figures [P1]** by adding a dashboard-figure exporter
and inserting two 300-DPI figures into the report. He then concluded that chat. So at my start
there were **no active chats needing a reply**, and the **only remaining required deliverable was
the Reproducibility Packet**.

### What was accomplished

**1. Built the Reproducibility Packet** (`deliverables/reproducibility_packet/`), the final
unbuilt deliverable. It contains:

- **`README.md`** — the top-level walkthrough for a cold outside reader with no project context.
  It walks from the public dataset download (G-Node DOI `10.12751/g-node.d76994`, CC BY-SA 4.0)
  → a Python 3.11 virtual environment and pinned dependencies → the **full 11-step pipeline in
  order**, with the exact command line for every script and a note of what each one writes →
  an **expected-results table** carrying the load-bearing numbers so a reader can confirm their
  run matches → a short section on why a clean negative is a genuine result → licensing,
  attribution, and a citation block → scope and limitations. It contains no local machine paths,
  no Collaboration Station framing, and no session history; the dataset directory is a
  `<DATA_NIX>` placeholder throughout, exactly as the Standards require.
- **`requirements.txt`** — the packet's own pinned dependency list (every library
  commercial-use-permitted, licenses documented inline).
- **`.gitignore`** — the packet's own ignore file, separate from the repository-root one, that
  keeps the shipped dashboard tracked while ignoring locally regenerated dashboards and any data
  a reader might stage inside the folder.
- **`LICENSE`** — **MIT** for the project's code (chosen over Apache-2.0 per the Claim Sheet's
  "lean: MIT or Apache-2.0"; MIT is the simplest and is commercial-use friendly), with an
  explicit note that it does not cover the CC BY-SA 4.0 dataset.
- **`verification_dashboard.html`** — the Slot 8 director's-verification artifact, placed as the
  reader's **first way in** (Section 1 of the README points there before anything else). It is the
  headline EEGNet dashboard and is fully self-contained (I grepped to confirm it makes no external
  network requests, so it opens offline in any browser).

**2. Validated the documented commands** against the existing intermediate outputs, running them
verbatim from the README (the cheap, dataset-free stages):

- `summarize_subject_statistics.py …` reproduced the headline statistics exactly: mean
  improvement **+0.023**, **5/9** subjects above the strongest control, min leave-one-out mean
  **−0.001**, headline success **not met**.
- `run_mtl_confirmatory_coupling_gate.py …` reproduced the Part B gate result exactly:
  **gate failed**, schedule-residualized mean **+0.011**, **4/9** positive, sign-flip p **0.746**.
- `render_verification_dashboard.py …` produced a dashboard that is **byte-identical (SHA-256)** to
  the copy shipped in the packet — confirming the entry-point artifact regenerates exactly from
  the documented command.

**3. Opened a review chat** (`chats/Claude-Codex/Reproducibility Packet Review/`) handing the
packet to Codex (it is co-owned) and asking him to (a) review/approve the packet and (b) give the
Technical Report its explicit final-deliverable approval, since its README still reads DRAFT even
though [P1]/[P2]/[P3] are all closed. Those two confirmations are the remaining Phase 3 gate.

**4. Cross-review** (Project Details requirement): I read Codex's HumanReport12 and his Session 12
working files. See below.

### Cross-review of Codex Session 12

I read Codex's most recent report (HumanReport12) and his S12 changes. His one substantive edit to
my Accessible Piece — changing the Part A wording from "most models barely edged above the strong
shortcut" to "the simpler models all fell short of the strong shortcut" — is **more accurate than
what I wrote**, because EEGNet was the *only* model rung above the strongest behavioral control on
the mean; the simpler models were below it. I agree with the change and carried that framing into
the packet README's expected-results section. His [P1] figures and [P3] bibliography approval are
sound. No corrections to propagate.

### Important decisions

- **Did not duplicate `scripts/`/`utils/` into the packet folder.** Copy-pasting the codebase into
  the packet would fork it and violate the no-copy-paste Standard; the "clone the repository and
  reproduce" bar is met by the repository as a whole. The README treats the repo as the
  reproduction unit and references code by repo-root-relative paths, with a clear "run from the
  repository root" instruction. I flagged this design choice to Codex explicitly in case he wants
  the packet to instead be a self-contained subtree — a point to settle before close, not after.
- **Chose MIT over Apache-2.0** for the code license (Claim Sheet left it as either; MIT is leaner).
- **Did not declare Phase 3 closed.** All three deliverables now exist, but Phase 3 closes only when
  every deliverable is explicitly approved by both agents. The packet is co-owned and unreviewed by
  Codex, and the Technical Report still lacks an explicit final-approval stamp. So this session
  hands those off rather than closing the phase. (No Phase-3-close progress report was written for
  the same reason.)

### Challenges and how they were handled

- **Getting the pipeline commands exactly right.** The reproduction value of the packet depends
  entirely on the documented commands being correct. I extracted every script's `argparse`
  signature and defaults directly from source rather than from memory, and caught a non-obvious
  ordering dependency: `build_features.py` consumes `montage_intersection.json`, which is produced
  by `audit_trial_counts.py`, **not** by `build_trial_metadata.py` — so the audit step must run
  before feature building. I also caught that `build_features --montage` takes
  `montage_intersection.json` while `audit_trial_counts --montage` takes `scalp_montage.json`;
  these are different files and mixing them would break a reader's run. The README orders the steps
  to respect these dependencies.
- **Citation accuracy.** My first draft of the dataset citation used an author list from memory; I
  corrected it against the verified `references.bib` entry (`boran2020dataset`) before finalizing.
- **Could not run a clean-room end-to-end reproduction this session.** The dataset-dependent and
  slow stages (NIX read, feature build, the EEGNet leave-one-subject-out loop) need the external
  dataset drive and ~tens of minutes of compute; I validated the final-stage commands and the
  entry-point artifact exactly, and named the full clean-room run as the one remaining validation
  gap for Codex to coordinate on.

### Files created or updated

- `deliverables/reproducibility_packet/README.md` — new; the top-level reproduction walkthrough.
- `deliverables/reproducibility_packet/requirements.txt` — new; packet-local pinned dependencies.
- `deliverables/reproducibility_packet/.gitignore` — new; packet-local ignore file.
- `deliverables/reproducibility_packet/LICENSE` — new; MIT license for the code.
- `deliverables/reproducibility_packet/verification_dashboard.html` — new; the self-contained Slot 8
  verification dashboard (headline EEGNet run) as the reader's entry point.
- `chats/Claude-Codex/Reproducibility Packet Review/Reproducibility Packet Review - Active.md` —
  new; review handoff to Codex.
- `agents/Claude/README.md` — refreshed for Session 11.
- `agents/Claude/Session Summaries/HumanReport11.md` — this report.
- `agents/Claude/Summary of Only Necessary Context.md` — rewritten at closeout.

I also committed Codex's completed Session 12 working-tree files (he still cannot push from his
sandbox), bundled with my Session 11 work.

### Next steps / pending actions

1. **Codex reviews the Reproducibility Packet** and either approves it or requests changes
   (active chat: *Reproducibility Packet Review*). Settle the "reference-the-repo vs.
   self-contained-subtree" design question if he disagrees with my call.
2. **Codex gives the Technical Report its explicit final-deliverable approval** (its README still
   says DRAFT though all its open items are closed).
3. **A clean-room end-to-end reproduction run** to fully satisfy the Standards "validate on a fresh
   environment" clause — the one validation I could not do this session. Coordinate on who runs it.
4. **Once all three deliverables are approved by both agents, Phase 3 closes** and whoever writes
   the closing turn writes the *Phase 3 Close* progress report. After that, per Project Details, the
   project is complete as scoped and no new work should be started without an explicit director
   signal.
