# EEG to LFP

**Can cheap scalp EEG tell you what a deep brain structure is doing?** For the specific thing we tested, on the specific hardware most people can afford: **no — and we can tell you exactly where the wall is.**

*A research project from [Dandelion Engineering](#about-dandelion-engineering). Self-directed: no client, no customer, no commission. **The research, the analysis, and this README were done by AI agents** — see [Who did this work](#who-did-this-work).*

---

## The result, in one paragraph

The long-term goal behind this project is what you might call "electrical fMRI" — recovering a picture of deep-brain activity from cheap, accessible scalp EEG plus machine learning. That goal spans many projects. This one ran the smallest useful first step: using an open dataset of **simultaneous** scalp EEG and intracranial recordings from nine epilepsy patients doing a memory task, we asked whether scalp EEG carries a **subject-transferable** signature of memory *load* in the medial temporal lobe — that is, whether a model trained on some people works on a person it has never seen.

**Part A is a clean negative.** We pre-registered a ladder of model classes — regularized logistic regression, filter-bank covariance, Riemannian classifiers, and a compact EEGNet-class neural network — and declared in advance how much a model had to beat the strongest non-signal control by. None of them did. The best (EEGNet) reached **+0.023 balanced accuracy against a pre-declared bar of +0.075**, and the entire positive mean was carried by a single subject, which failed the robustness clause we had written before seeing any result. **The binding constraint is the 8-channel common montage plus cross-subject transfer, not the model class** — and the report shows the work that localizes it there rather than asserting it.

**Part B is an exploratory lead, and it is labelled exploratory because it did not validate.** The intracranial memory-load substrate we were looking for is real (7 of 9 subjects, *p* = 0.016). The strongest scalp decoder's output showed a raw positive coupling to it that the weaker linear decoders did not — but that coupling **did not survive residualization** for load and task schedule, so at nine subjects it cannot be cleanly separated from a shared task-linked correlate. A confirmatory gate with fixed criteria was written in advance and **failed clearly**. The report says so in its abstract.

**Both outcomes were named as pre-declared success and failure shapes before any result was observed.** That is the point of the project, and it is why a negative is worth publishing.

## The most interesting thing in here is the control

The strongest non-signal control turned out to be almost entirely **previous-trial correctness**, scoring 0.596 across 9 of 9 subjects. That is not leakage — it is a rule of the task. An incorrect trial forces a low-load trial next, so after an error the current trial is high-load 2 times in 130, versus 1021 in 1523 after a correct one. The schedule of the experiment carries information about the load of the next trial, and any model can pick that up without reading a single thing about the brain.

**A weaker write-up would have reported 0.616 against chance and called it a decoder.** If you take one methodological thing from this repository, take that.

## Read it

| | |
|---|---|
| **The science in plain language** | [`deliverables/accessible_piece/Accessible Piece.md`](deliverables/accessible_piece/Accessible%20Piece.md) |
| **The full technical report** | [`deliverables/technical_report/main.pdf`](deliverables/technical_report/main.pdf) (LaTeX source beside it) |
| **Reproduce it yourself** | [`deliverables/reproducibility_packet/`](deliverables/reproducibility_packet/) |
| **What the project promised before it started** | [`Claim Sheet.md`](Claim%20Sheet.md), and [`Accessible Claim Sheet.md`](Accessible%20Claim%20Sheet.md) in plain language |

The Claim Sheet is worth opening even if you skip the report. It is the contract the project was held to — the models to be tried, the controls, the statistical tests, and the success, failure, and inconclusive shapes, all written down **before any result existed**. The result above is what happens when you hold yourself to one of those.

## Reproducing it, stated honestly

**The packet reproduced the report's numbers twice, independently, on 2026-06-12.** The second run is the one that matters: a different agent, working from a clean output tree, following the packet's own README. It reproduced the headline balanced accuracy of 0.616, and the regenerated verification dashboard and statistics summary were **byte-identical** to the ones shipped here.

**Two things about that have not been tested, and we would rather say so than let you find out:**

- **Both runs were on the same machine the work was written on.** The pinned dependencies resolve there. Nobody has confirmed they resolve on another OS, another Python, or without that GPU.
- **Both runs used a local copy of the dataset.** Nobody has downloaded the archive fresh from the DOI and confirmed it unpacks into the layout the packet expects.

Those limits do not take anything away from what the two runs established — the numbers in the report were regenerated from the packet, twice, once by an agent working from a clean tree. What they bound is how far that evidence reaches: portability to another environment, and a clean run starting from the DOI rather than from a copy already on disk, are both untested. If either one bites you, opening an issue is genuinely useful to us.

## The data

Boran et al. (2019), distributed publicly through G-Node under DOI [`10.12751/g-node.d76994`](https://doi.org/10.12751/g-node.d76994) — nine epilepsy patients with simultaneous scalp EEG, intracranial medial-temporal-lobe recordings, and single units, performing a verbal working-memory (Sternberg) task. De-identified, already public, and not collected by us.

**Licensing.** The dataset is **CC BY-SA 4.0**. No raw data is redistributed here; the packet points at the DOI. Our analysis code is **MIT** and ships with the packet. The report and figures carry attribution to Boran et al. (2019).

## Who did this work

**This project was run by AI agents.** Two of them — named Claude and Codex in the repository — did the analysis, wrote the code, ran the models, and wrote the Technical Report. **Randy Crespo** directed it: he set the question, approved the Claim Sheet, and made the decisions that belong to a person. **This README was written by an AI agent too**, and reviewed by the other one before it was published.

We say this plainly because the report's own author line does not, and because you should know it before you weigh anything in here. It is not a disclaimer and it is not an apology — it is how this company works, and the whole repository is open so you can judge the result on its own terms.

## About this project's history

This is an **early** Dandelion project. It ran in June 2026, and the framework the company uses to run research has changed since — later projects carry artifacts and checks this one did not have. The science is unaffected: what is written here is what the project found, reported the way it reported it.

## About Dandelion Engineering

Dandelion Engineering is a small research and technology company with one purpose: **to do real research, and turn what we learn into affordable technology that materially improves the lives of everyday people.**

The name comes from Carl Sagan's *Cosmos*, where a dandelion seed serves as the ship of the imagination — small, durable, carried far by the wind, able to take root almost anywhere.

We are not building software for software companies, and we are not optimizing workflows for incremental gains. We are pointing this generation of AI at science, at engineering, and at things an individual or a family could actually use. The test is whether someone's daily life would be better if the work succeeded. If the answer is no, it is not for us.

**We publish the work, including when it fails.** Negative results, dead ends, and our own mistakes get written up and shipped as readily as the successes. This is not modesty and it is not a content strategy — it is the only thing that makes a small company's claims checkable. Anyone can say they did careful research. Almost nobody publishes the run that did not pan out, or hands over the scripts that would let you prove them wrong.

**This repository is one of those runs.**

## Contact

**Randy Crespo** — Founder, Dandelion Engineering
[randy@dandelionengineering.com](mailto:randy@dandelionengineering.com)
[www.linkedin.com/in/randy-crespo](https://www.linkedin.com/in/randy-crespo)
