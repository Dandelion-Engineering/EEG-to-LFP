# Licensing and Citation

This file is a **scope record**, not a license. It maps which parts of this
repository fall under which license, records the dataset boundary, and tells you
how to cite the work. The licenses themselves are the standard instruments in
`LICENSE` (MIT) and `LICENSE-docs` (Creative Commons Attribution 4.0
International). Where this record and a license text ever disagree, the license
text governs.

## The three licenses in play

- **Code → MIT** (`LICENSE`). Covers all Dandelion-owned source code, scripts,
  configuration, and software-like reproducibility machinery. Permissive and
  commercial-use-permitting.
- **Prose → CC BY 4.0** (`LICENSE-docs`). Covers all Dandelion-owned written and
  narrative artifacts. Attribution required; commercial use permitted; no
  ShareAlike obligation.
- **The dataset, and the derived extract of it this repository ships → the
  dataset's own CC BY-SA 4.0.** The dataset
  this project analyzes is licensed CC BY-SA 4.0. We do not redistribute the raw
  recordings, but the verification dashboard does embed a derived trial-level
  extract of them, and two committed figures plot quantities computed from them.
  The extract carries the dataset's own terms; the two figures are offered under
  CC BY-SA 4.0 voluntarily. See **Dataset boundary** below, which says which is
  which and why the difference matters.

## Scope

**MIT (`LICENSE`)** covers Dandelion-owned:

- `scripts/` and `utils/` — every analysis, model, and audit script
- `requirements.txt` at the repository root and in the reproducibility packet
- `.gitignore` at the repository root and in the reproducibility packet
- **everything in `deliverables/reproducibility_packet/`**, including its
  `README.md` and the markup of `verification_dashboard.html`

`deliverables/reproducibility_packet/LICENSE` is a copy of this same MIT license
carrying a scope note, and it predates this file. **That note is why the whole
packet directory is MIT here, including its prose.** The note covers "the
contents of `scripts/`, `utils/`, and this reproducibility packet," and the
packet's own `README.md`, Section 8, says the same. This file follows those
rather than narrowing them: a scope record that contradicted a license already
sitting in the tree would be worse than one that applies a permissive license a
little more widely than a documentation license would reach. MIT grants strictly
more than CC BY 4.0, so no reuser is disadvantaged by it.

**CC BY 4.0 (`LICENSE-docs`)** covers Dandelion-owned:

- `AgentPrompt.md` and `Project Details/Project Details.md`
- `Claim Sheet.md` and `Accessible Claim Sheet.md`
- `deliverables/technical_report/` prose — `main.tex`, `references.bib`,
  `README.md`, and the compiled `main.pdf`, except for the two figures named
  below
- `deliverables/accessible_piece/Accessible Piece.md`
- READMEs, progress reports, session summaries, and the narrative material
  under `agents/`
- the concluded chat records under `chats/`
- `director_requests.md`
- `README.md`, `LICENSING.md` (this file), and `CITATION.cff` at the repository
  root

**`LICENSE` and `LICENSE-docs` are the standard license instruments themselves**,
reproduced unmodified. They are not Dandelion-authored material and neither file
licenses the other.

**Anything Dandelion owns that is not named above** falls under MIT if it is code
or configuration and CC BY 4.0 if it is prose. This catch-all exists so that a
path added later is covered by default rather than silently unlicensed.

## Dataset boundary

**The raw recordings are not redistributed by this repository. A derived
trial-level extract is.** Those are two different answers and this section gives
both, because a reuser needs the second one.

**Not redistributed:** no raw electrophysiology file is tracked here. You
download the dataset yourself from the G-Node DOI; the reproducibility packet's
README, Section 2, tells you how.

**Redistributed:** `deliverables/reproducibility_packet/verification_dashboard.html`
embeds **1,683 trial-level records** — subject, session and trial identifiers,
the ground-truth label, the set size, and the model and control outputs for each
trial — carried in HTML `title` attributes across nine per-subject strips and ten
tables. That is a derived extract of the dataset, and publishing this repository
publishes it. **If you reuse that data layer, attribute the dataset authors and
observe the dataset's own CC BY-SA 4.0 terms.** Dandelion's markup and expression
around it are MIT.

The dataset is:

> Boran, E., Fedele, T., Steiner, A., Hilfiker, P., Stieglitz, L., Grunwald, T.,
> Sarnthein, J. (2019). *Dataset of simultaneous scalp EEG and intracranial EEG
> recordings and human medial temporal lobe units during a verbal working memory
> task.* G-Node. https://doi.org/10.12751/g-node.d76994 — licensed
> **CC BY-SA 4.0**: https://creativecommons.org/licenses/by-sa/4.0/

Its descriptor paper is a separate work with a separate license, cited under
**Third-party material** below. The dataset and the paper are often referred to
interchangeably; they are not the same object, and their years, titles and
licenses differ.

**What ShareAlike does and does not settle.** CC BY-SA 4.0 requires *adapted
material* to be shared under a compatible license, and its Section 4 reaches Sui
Generis Database Rights. Creative Commons' own guidance is that a report
summarizing a database without republishing its elements generally does not
engage those rights, and that the ShareAlike branch of Section 4 concerns reuse
of all or a substantial portion of a database **in another database**. So we do
not claim that every number in this repository that came from the data is
CC BY-SA 4.0 — that would overstate the source license, and the people most
likely to rely on it are the ones we would be misleading.

What we do instead:

- **The data layer above carries the dataset's own terms.** We are describing the
  source license, not granting one.
- **We voluntarily offer these two figures under CC BY-SA 4.0** —
  https://creativecommons.org/licenses/by-sa/4.0/ — rather than the
  CC BY 4.0 that covers the prose around them. They are Dandelion's expression
  and ours to license; if ShareAlike does turn out to reach them, the obligation
  is already met.

- `deliverables/technical_report/figures/eegnet_raw_all_subject_improvements.png`
- `deliverables/technical_report/figures/eegnet_raw_all_mtl_coupling_residualization.png`

**An isolated statistic quoted in prose is not, by itself, either of those
things.** Attribute the dataset when you reuse the data layer or a
dataset-derived figure; you do not need a ShareAlike license to quote a result.

**The surrounding prose stays CC BY 4.0.** CC BY-SA 4.0 permits licensed material
to be included in a *collection* without the ShareAlike condition reaching the
rest of that collection. The technical report is Dandelion's own prose with two
attributed figures embedded in it; the figures carry CC BY-SA 4.0 and the report
around them does not.

**If you reuse the data layer or either of the two figures named above,
attribute both:** this project, and the dataset. **An isolated number quoted from
the report is not covered by that**, and does not become ShareAlike by having
been derived; cite the work as you would cite any other source.

## Third-party material

`Project Details/Dataset of human medial temporal lobe neurons, scalp and
intracranial EEG during a verbal working memory task.pdf` is **not ours to
license.** It is the publisher's PDF of the dataset's descriptor paper,
redistributed here unmodified:

> Boran, E., Fedele, T., Steiner, A., Hilfiker, P., Stieglitz, L., Grunwald, T.,
> Sarnthein, J. (2020). Dataset of human medial temporal lobe neurons, scalp and
> intracranial EEG during a verbal working memory task. *Scientific Data* **7**,
> 30. https://doi.org/10.1038/s41597-020-0364-3
>
> © The Author(s) 2020. Licensed under Creative Commons Attribution 4.0
> International: https://creativecommons.org/licenses/by/4.0/ — no changes were
> made.

Neither `LICENSE` nor `LICENSE-docs` relicenses it, and neither relicenses the
dataset.

**Software dependencies** all carry licenses permitting commercial use: NumPy,
SciPy, h5py, nixio, pandas, scikit-learn (BSD-family); matplotlib (PSF,
BSD-compatible); pyarrow (Apache-2.0). Pinned versions are in
`requirements.txt`.

## How to attribute (CC BY 4.0)

A reuser of the prose satisfies attribution with:

> "EEG to LFP" by Dandelion Engineering, licensed under CC BY 4.0. Source:
> https://github.com/Dandelion-Engineering/EEG-to-LFP. Changes, if any, noted.

## How to cite this work

The work is directed by one human, Randy Crespo, and produced in collaboration
with two AI research agents, Claude (Anthropic) and Codex (OpenAI). Under current
citation and publishing norms an AI system is not listed as a formal author
because it cannot take responsibility for the work; the accountable, citable
author is the human. In keeping with Dandelion Engineering's transparency
standard, the AI collaboration is **disclosed**, not hidden. So: cite Randy
Crespo (with Dandelion Engineering as the organization), and disclose the AI
agents in a note.

The machine-readable `CITATION.cff` in the repository root is the canonical
source GitHub uses for its "Cite this repository" button. Human-readable forms:

**Plain / APA-style**

> Crespo, R. (2026). *EEG to LFP: a bounded first rung toward "electrical fMRI"*
> (Version 1.0.0) [Software]. Dandelion Engineering.
> https://github.com/Dandelion-Engineering/EEG-to-LFP. Produced in collaboration
> with the AI research agents Claude (Anthropic) and Codex (OpenAI).

**BibTeX**

```bibtex
@misc{dandelion_eeg_to_lfp_2026,
  author       = {Crespo, Randy},
  title        = {EEG to LFP: a bounded first rung toward ``electrical fMRI''},
  year         = {2026},
  howpublished = {Dandelion Engineering},
  url          = {https://github.com/Dandelion-Engineering/EEG-to-LFP},
  note         = {Version 1.0.0. Produced by Randy Crespo in collaboration with
                  the AI research agents Claude (Anthropic) and Codex (OpenAI).}
}
```
