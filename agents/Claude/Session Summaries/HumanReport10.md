# Claude — Human Report 10

**Current Date and Time:** 2026-06-12 11:40 PDT

## Summary

This was a Phase 3 (Deliverables) session. The project's analysis is settled — the two-part result is locked in under Amendment 1 — so the work now is producing the three required public artifacts (Technical Report, Accessible Piece, Reproducibility Packet). I came in with the Technical Report already drafted (my Session 9) and, as of Codex's Session 11, its Part B confirmatory-test placeholder filled in. My job this session was to push the deliverables forward. I did two substantive things and verified a third.

### 1. Wrote the Accessible Piece (the headline contribution)

The Accessible Piece is the second of the three required deliverables and the last one that hadn't been started. It's the plain-language companion to the Technical Report — same project, written for a reader with no technical background. I wrote it end to end:

- **File:** `deliverables/accessible_piece/Accessible Piece.md`
- It walks the full story without assuming any prior knowledge: the "electrical fMRI" dream (cheap scalp cap + AI to glimpse the deep brain), why deep-brain readout from the scalp is genuinely hard (the skull blurs everything), the one reason for hope (the deep brain talks to the cortex, which EEG *can* see), and the rare dataset that made the test possible (simultaneous inside-and-outside recordings from the same brains).
- It then explains, in plain terms, what we actually tested (can a computer read working-memory load from the scalp on a person it's never seen, and is that tied to real deep activity), and — the part I spent the most care on — *how we kept ourselves honest*: testing on unseen people, comparing against the sneaky "previous-trial" task shortcut rather than against a coin flip, and writing down the success bar before looking at any answer.
- The results section gives both parts straight: **Part A**, a clean "no" (and why — it's the few shared sensors plus the demand that one model fit everyone, not weak AI), framed explicitly as a *useful* negative that maps where the wall is; and **Part B**, the tantalizing lead (our best model seemed to echo a real deep-brain memory rhythm) that we then tried hard to kill and could not confirm — reported honestly as exploratory, not proven, citing Codex's failed confirmatory gate.
- Every term a layperson wouldn't know (fMRI, EEG, medial temporal lobe, working memory, the Sternberg task, leave-one-subject-out, the replication crisis) carries a link to a credible source so the reader can go deeper without getting stuck.

I was careful not to oversell. Part B in particular is framed strictly as "a lead worth chasing with more data," never as a deep-brain readout that works. The piece closes by pointing the long-term effort at its two concrete takeaways: the first wall has been identified, and the most promising next signal has been named.

### 2. Closed the Technical Report's bibliography item [P3]

The Technical Report had three flagged open items after my Session 9 draft. Codex closed [P2] (the Part B confirmatory test) in his Session 11. This session I closed **[P3]**, the joint reconciliation of both agents' reference lists into the report bibliography:

- Cross-checked both `agents/Claude/references.md` and `agents/Codex/references.md` against `deliverables/technical_report/references.bib`. Every citation the report actually uses (9 of them) is present with a verified DOI.
- Uncited context sources (foundation-model audits, source-imaging background, the dataset's license legal text) are intentionally kept in the per-agent reference files rather than the report bibliography — the report doesn't cite them, and the bibliography style only prints cited works, so adding them would be noise.
- Fixed the one bibliography entry that had a placeholder author list (the NeuroFlowNet prior-art paper) using the real authors Codex had recorded, and added its DOI.
- Updated the `.bib` header note and the technical-report `README.md` to record [P3] as complete, pending Codex's final approval as the report's reviewer.

### 3. Verified the Technical Report still builds

After editing the bibliography I rebuilt the report locally (pdflatex → bibtex → pdflatex ×2). It compiles cleanly: no undefined references, no citation warnings, produces the full PDF. (Codex's Session 11 hit a broken local LaTeX install in his sandbox; my environment's MiKTeX works, so I confirmed the build on my side.)

### Coordination

I opened a chat thread, `chats/Claude-Codex/Accessible Piece Review/`, handing Codex the Accessible Piece for review/approval (the default convention is that I write the narrative docs and he approves them) and asking him to confirm the [P3] reconciliation. I flagged two specific things for him to check: that I haven't overstated Part B anywhere, and that my plain-language explanation of *why* Part A failed matches his read of the diagnostics.

## Challenges and how they were handled

No real obstacles this session. The main judgment call was tone in the Accessible Piece: the honest result is a negative plus an unconfirmed lead, which is easy to write in a way that either sounds like a disappointment or, worse, quietly inflates the lead into a finding. I leaned into the framing that a clean, well-understood negative is a genuine contribution (it redirects the long-term effort early and cheaply), and I kept Part B explicitly in "exploratory, not proven" language throughout, anchored to Codex's failed confirmatory gate. That keeps the piece engaging and honest at the same time.

## Important decisions

- **Accessible Piece location and format:** `deliverables/accessible_piece/Accessible Piece.md`, Markdown, sibling to `deliverables/technical_report/`. Markdown (not LaTeX) because the Accessible Piece is for general readers and benefits from clickable inline source links; only the Technical Report is required to be LaTeX.
- **[P3] scope:** reconcile into the *report bibliography* only what the report cites; leave uncited context sources in the per-agent reference files. This keeps the bibliography honest and clean rather than padded.
- **Did not start the Reproducibility Packet this session** — it's a substantial co-owned artifact and deserves its own focused pass. Flagged as my likely next-session lead.
- **Did not touch the Claim Sheet or Accessible Claim Sheet** — Amendment 1 already covers the project direction and nothing this session changed it.

## Files created or updated

- `deliverables/accessible_piece/Accessible Piece.md` — **created.** The Accessible Piece deliverable (full plain-language write-up of the two-part result).
- `deliverables/technical_report/references.bib` — updated: [P3] reconciliation note in header; NeuroFlowNet entry given real authors + DOI.
- `deliverables/technical_report/README.md` — updated: [P3] moved from open to completed (pending Codex approval).
- `chats/Claude-Codex/Accessible Piece Review/Accessible Piece Review - Active.md` — created: handed the Accessible Piece to Codex for review and asked him to confirm [P3].
- `agents/Claude/README.md` — updated for Session 10 (workspace state).
- `agents/Claude/Summary of Only Necessary Context.md` — rewritten at closeout.
- `agents/Claude/Session Summaries/HumanReport10.md` — this report.
- Also committed alongside mine (Codex couldn't push from his sandbox): his completed Session 11 working tree — `scripts/run_mtl_confirmatory_coupling_gate.py`, `scripts/render_verification_dashboard.py`, `deliverables/technical_report/main.tex` (§5.2 confirmatory result), `deliverables/technical_report/README.md` ([P2] note), his `README.md`, `Summary of Only Necessary Context.md`, and `HumanReport11.md`.

## Cross-review (per the Working Method)

I read Codex's most recent report (`HumanReport11.md`) and his Session-11 work. He closed Part B correctly and strictly: his confirmatory gate fixed the metric to the schedule-residualized coupling and required positive mean, ≥7/9 subjects, two-sided sign-flip p≤0.05, and all leave-one-out means above zero — and it failed clearly (mean +0.011, 4/9, p=0.746, min LOO −0.010). This is exactly the strict, non-promotional resolution Part B needed; I agree with it and built the Accessible Piece's Part B framing directly on top of it. No corrections — corrections propagate forward, and there was nothing to correct.

## Next steps / pending actions

1. **Reproducibility Packet** (co-owned) — the last unbuilt required deliverable. Needs: a top-level README walking an outside reader from the public dataset download (G-Node DOI) through reproducing every result, with the verification dashboard as the first way in; its own `requirements.txt`, `.gitignore`, and code license (MIT or Apache-2.0). No raw data in the repo. I'll likely take a first pass next session.
2. **Technical Report [P1]** — insert verification-dashboard figures at ≥300 DPI. The dashboard currently renders as HTML, so this needs a render-to-image step; co-owned with Codex, coordination flagged in the review chat.
3. **Codex's review** of the Accessible Piece and confirmation of [P3] — pending in the review chat.
4. When Phase 3 formally closes, whoever closes it writes a Progress Report (an extra trigger); my next *cadence* progress report is at my Session 16.
