# Progress Report — Amendment 1 (Decoding-to-Coupling Re-point)

**Agent:** Claude
**Date/Time:** 2026-06-12 09:15 PST
**Trigger:** Approved amendment to the Claim Sheet (Amendment 1, ratified this session).
**For:** Randy (the director). Written to be read start to finish without looking anything up.

> This is a focused report on a single event: the project's plan officially changed today. For the full background on the results that led here — the model ladder, EEGNet, the success bar — see my **Progress Report Session 8** (written earlier today). This report covers what's *new* since that one (a sharper test of the deep-brain lead) and exactly what changed in the project's contract.

## The one-paragraph version

Today the two AI agents formally agreed to change the project's plan, through the project's amendment process. The change: the project's headline shifts from "scalp EEG can read memory load" (which we tested thoroughly and found it *can't*, for this 8-channel setup across people) to a **two-part honest result** — (A) a clean, well-mapped "here's where the wall is" finding, and (B) a promising-but-unproven lead that the scalp signal is tied to deep-brain memory activity. The single most important thing to know: **we did not lower the original passing grade to manufacture a win.** Both of these outcomes were written down as named possibilities *before* we ran anything; we're simply reporting which ones came true. This is the honesty machinery working exactly as designed.

## The one new piece of evidence since this morning's report

After I posted the EEGNet results, my collaborator Codex ran a sharper test on the deep-brain "coupling" lead — and it's the reason we narrowed the claim rather than overselling it. It's worth understanding because it's a textbook example of how a result can look real and still not be.

The encouraging finding was: our best scalp model's output *tracked* the deep memory rhythm in 7 of 9 people. The obvious worry: maybe the scalp output and the deep rhythm line up simply because **both** rise and fall with "the task is hard right now" — not because the scalp is genuinely echoing the *deep* signal specifically. That would be a shared by-product, not a real deep readout.

Codex tested this directly with a technique called **[residualization](https://en.wikipedia.org/wiki/Partial_correlation)** — statistically subtracting out the "obvious" explanations and seeing whether any connection survives. Here's what happened (these are correlations; closer to 0 means "no connection left"):

| What we removed before checking the connection | Connection remaining | In how many people |
|---|---|---|
| Nothing (the raw, encouraging number) | 0.068 | 7 of 9 |
| Memory load itself | 0.050 | 5 of 9 |
| Load **+ the task's schedule structure** | **0.011** | 4 of 9 |
| Load + schedule + behavior/timing | 0.013 | 5 of 9 |

The connection **mostly dissolves** once you control for the task's structure. I independently re-ran Codex's test and got the identical numbers, so the finding is solid.

Now, the honest subtlety — and this is why we say "unproven" rather than "disproven": if the deep brain signal is *genuinely* load-linked (which the literature says it is), then subtracting out load will *also* subtract out part of the real shared signal we're trying to detect. So this test can't cleanly separate "a faint real deep signal" from "a task-difficulty by-product." With only 9 people, this dataset simply can't settle it. The right call is to report the lead as **exploratory** — the most promising next thing to chase — not as a discovery. That's what the amendment does.

## Exactly what changed in the contract

The project's plan (the "Claim Sheet") was amended — appended to, never overwritten, so the original is preserved as a record. In plain terms:

1. **The headline claim was re-pointed** from a single "scalp beats baseline + it's deep" claim to a **two-part result**: (A) a clean negative boundary for the decoding, and (B) the exploratory deep-coupling lead.
2. **The original passing grade was left exactly as it was** — tested, not met, not softened. (This is the part I most want you to sanity-check, because it's the integrity-critical one.)
3. **Two "stretch goal" analyses we'd planned were formally shelved** — they were always conditional on the decoding succeeding first, and it didn't, so per the original rules they don't run. This keeps the project from sprawling.
4. **A sharper follow-up test was defined** for the deep-coupling lead (Codex's task), with the stricter controls built in *from the start* so it can't flatter itself.
5. **Nothing we built was thrown away.** All the analysis still stands — the decoding runs are now the evidence for Part A, and the coupling runs are the evidence for Part B. Nothing got archived or deleted.

Both the technical plan and your plain-language companion document (`Accessible Claim Sheet.md`) were updated in the same session so they stay in sync.

## How this happened (the collaboration working)

This is a good example of the two-agent setup doing its job. I proposed the re-point based on the EEGNet results. Codex agreed the decoding half was done — but pushed back on my wording for the deep-coupling half, saying "validating that the scalp carries deep information" was too strong for the evidence. He was right, and he backed it with the residualization test above. I adopted his narrower language wholesale. The disagreement got settled in one round, in chat, before either of us touched the project's contract — which is exactly how it's supposed to go.

## Where the project stands now, and what's next

The project now has a **complete, concludable result** — a clean negative plus a documented lead. The next stretch is likely:

1. Codex's one focused, pre-registered confirmation test on the coupling lead.
2. Then **the write-up phase**: the Technical Report (for scientists), the Accessible Piece (the full story for any reader), and the Reproducibility Packet (code + your verification dashboard, so anyone can check our work). We haven't formally opened that phase yet, but it's the natural next step.

## Why this is a real contribution

Dandelion's whole premise is that an honest "no," clearly mapped, is worth as much as a "yes" — because it stops the next, bigger effort from making a wrong turn. We set out to find the smallest honest first rung toward the long-term "electrical fMRI" vision. We learned that *this particular* rung (8 scalp channels, 9 people, reading across people) doesn't bear weight — and, along the way, we identified the most likely *next* foothold (the deep theta-alpha coupling, tested with more statistical power). That is precisely the kind of durable, honest result the project's slow, no-rush method is built to produce.

## Where the files are

- **Your plain-language plan, now amended:** `Accessible Claim Sheet.md` (project root) — read the new "Amendment 1" section at the bottom.
- **The technical contract, now amended:** `Claim Sheet.md` (project root) — see the "Amendment log."
- **This morning's fuller results report:** `agents/Claude/Progress Reports/Progress Report Session 8.md`.
- **The full decision conversation:** `chats/Claude-Codex/Riemannian Ladder Verdict/`.
