# Reproducibility Packet — Subject-Transferable Working-Memory Decoding from Scalp EEG, Validated Against Intracranial MTL Recordings

This packet lets an outside reader reproduce, from scratch, every number behind a single
research result: **does scalp EEG carry a *subject-transferable* signature of a deep
medial-temporal-lobe (MTL) working-memory state that a model can read out of a person it has
never seen?** The study tests that question on a public dataset of *simultaneous* scalp-EEG and
intracranial recordings from 9 people performing a verbal working-memory task, using a strict
leave-one-subject-out evaluation and a pre-declared set of controls and success thresholds.

The honest, pre-registered answer is a **two-part result**:

- **Part A — a clean, bounded negative.** Across a full ladder of model classes
  (regularized linear → filter-bank covariance → Riemannian → a compact CNN, EEGNet), an
  8-channel common-montage decoder does **not** beat the strongest non-signal control by the
  pre-declared margin under leave-one-subject-out evaluation. The best model (EEGNet) reaches
  a mean improvement of **+0.023** balanced accuracy over the strongest control (the bar was
  **+0.075**), is above that control in only **5 of 9** subjects (bar: 7 of 9), and its positive
  mean collapses to **−0.001** when the single best subject is removed (bar: stay above +0.04).
  This is a rigorously characterized boundary, not a failed experiment — it tells the larger
  research program where the wall is.
- **Part B — an exploratory mechanism lead that did not validate.** The strongest decoder's
  output shows a *suggestive* raw coupling to the simultaneously-recorded MTL theta−alpha load
  signal (positive in 7 of 9 subjects), but that coupling **does not survive** stricter
  residualization, and a fixed, pre-registered confirmatory gate on the schedule-residualized
  metric **fails clearly** (mean +0.011, 4/9 positive, sign-flip p = 0.75). Part B is reported as
  an exploratory next-signal-to-chase, not a finding.

Everything below reproduces both parts exactly.

---

## 1. Start here: open the verification dashboard

Before running anything, open the file **[`verification_dashboard.html`](verification_dashboard.html)**
in any web browser. It is a static, self-contained page (no server, no internet, no
dependencies). It is the fastest way to see the whole result the way the project's director
verifies it:

- A summary band at the top: mean decoder balanced accuracy, mean strongest-control balanced
  accuracy, mean improvement, how many of the 9 held-out subjects beat the control, the
  minimum leave-one-out mean, and whether the Part B mechanism gate passed.
- One panel per held-out subject — the subject the model never saw — showing the decoder's
  scalp-only prediction next to the control predictions on the same trials, a per-subject
  improvement number, and a plain-language verdict (does this subject **weaken** or
  **contradict** the claim).
- A mechanism line per subject describing the MTL theta−alpha coupling the scalp readout was
  tested against.

The dashboard shipped here is the **headline EEGNet run** (`eegnet_raw_all`). When you run the
pipeline in Section 5, you regenerate this exact file (and a companion one for the linear
model) yourself.

> **What "balanced accuracy" means.** Balanced accuracy is the average of the true-positive
> rate and the true-negative rate, so chance is 0.50 even when the two classes are uneven. We
> report decoder skill as *improvement over the strongest control*, not raw accuracy above
> chance — a model that merely re-learns a non-neural shortcut should score ~0 by this measure.
> ([scikit-learn: balanced accuracy](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.balanced_accuracy_score.html))

---

## 2. The dataset (download separately — not included here)

The raw data is **not** redistributed in this packet. You download it once from the public
archive.

- **Source:** Boran, Fedele, Steiner, Hilfiker, Stieglitz, Grunwald, Sarnthein — *Dataset of
  human medial temporal lobe neurons, scalp and intracranial EEG during a verbal working memory
  task.*
- **Archive (G-Node GIN), DOI:** [`10.12751/g-node.d76994`](https://doi.gin.g-node.org/10.12751/g-node.d76994/)
- **Dataset paper:** Boran et al., *Scientific Data* 7, 30 (2020) —
  [doi:10.1038/s41597-020-0364-3](https://doi.org/10.1038/s41597-020-0364-3)
- **License:** **CC BY-SA 4.0** — commercial use permitted *with attribution and ShareAlike on
  adaptations* ([license text](https://creativecommons.org/licenses/by-sa/4.0/)). See Section 8.

Download the repository from the DOI page and locate the **`data_nix/`** directory. It contains
37 session files in the NIX format (HDF5 under the hood), named
`Data_Subject_NN_Session_MM.h5`, covering 9 subjects. Every command below takes the path to that
directory as an argument; this README writes it as `<DATA_NIX>`. Substitute your own absolute
path (for example, on Windows, something like `E:\datasets\Simultaneous_EEG_LFP\data_nix`).

No file in this packet hard-codes a data path; the location is always passed on the command line.

---

## 3. Environment

- **Python 3.11** (the result was produced on 3.11.9).
- Dependencies are pinned in **[`requirements.txt`](requirements.txt)**. Every dependency is a
  permissively licensed library that allows commercial use (NumPy/SciPy/h5py/nixio/pandas/
  scikit-learn BSD-family; matplotlib PSF/BSD-compatible; pyarrow Apache-2.0). The two heavier
  modeling rungs — the Riemannian classifier and EEGNet — are **hand-implemented in NumPy** in
  the `utils/` module, so there is **no deep-learning framework dependency** (no PyTorch, no
  TensorFlow). This is a deliberate efficiency choice: the entire pipeline runs on a consumer
  laptop CPU.

Create and populate a virtual environment from the **repository root** (the directory that
contains `scripts/`, `utils/`, and `requirements.txt`):

**Windows (PowerShell):**
```powershell
py -3.11 -m venv venv
.\venv\Scripts\pip.exe install -r deliverables\reproducibility_packet\requirements.txt
```

**Linux / macOS:**
```bash
python3.11 -m venv venv
./venv/bin/pip install -r deliverables/reproducibility_packet/requirements.txt
```

In the commands below, the interpreter is written as `PYTHON`. Use `.\venv\Scripts\python.exe`
on Windows or `./venv/bin/python` on Linux/macOS. **Always use the virtual-environment
interpreter explicitly — never a bare `python`/`pip`** — so the pinned versions are the ones
that run.

---

## 4. Repository layout

All reproduction code lives at the repository root and is shared, imported, never copy-pasted:

```
utils/                       Shared library (imported by every script)
  nix_io.py                  NIX/HDF5 reader for the dataset
  epoching.py                Maintenance-window epoch alignment
  features.py                Band power + covariance feature extraction
  riemann.py                 Hand-rolled Riemannian geometry (rungs 2-3)
  eegnet.py                  Hand-rolled EEGNet, gradient-checked (rung 4)
  mechanism.py               MTL coupling / band-power helpers
scripts/                     One purpose per script, argparse, no hard-coded paths
deliverables/
  technical_report/          Full technical write-up (LaTeX) + figures
  accessible_piece/          Plain-language companion write-up
  reproducibility_packet/    This packet (README, requirements, license, dashboard)
outputs/                     Created by the pipeline (not tracked in version control)
```

Run every command from the **repository root**. Outputs are written under `outputs/` in
project-relative locations.

---

## 5. The pipeline — reproduce every number

Run these in order. Each script prints progress to stdout, writes named files under `outputs/`,
and fails loudly on bad input. Steps that read the raw dataset take `<DATA_NIX>`; later steps
read only the intermediate files produced by earlier steps. Total runtime on a consumer laptop
CPU is dominated by the EEGNet step (Section 5.6, tens of minutes for the 9 LOSO folds); every
other step is seconds to a few minutes.

### 5.1 Validate the dataset reader (stop-or-go gate)
```
PYTHON scripts/validate_nix_reader.py --file <DATA_NIX>/Data_Subject_01_Session_01.h5
```
Confirms the reader recovers sampling rates, offsets, and channel labels within tolerance before
any analysis runs. If this fails, stop and fix the environment — do not proceed.

### 5.2 Build trial metadata and the scalp montage
```
PYTHON scripts/build_trial_metadata.py --data-dir <DATA_NIX> --out-dir outputs
```
Writes `outputs/trial_metadata.csv` / `.parquet`, `outputs/session_summary.csv`, and
`outputs/scalp_montage.json` (the per-session channel sets).

### 5.3 Trial-count + montage audit (defines the common 8-channel montage)
```
PYTHON scripts/audit_trial_counts.py --metadata outputs/trial_metadata.csv --montage outputs/scalp_montage.json --out-dir outputs
```
Writes `outputs/trial_count_audit.{csv,md}` and, importantly, **`outputs/montage_intersection.json`** —
the 8-channel common montage (`A1 A2 C3 C4 F3 F4 O1 O2`) every subject shares, plus the
6-channel brain-only subset (refs A1/A2 removed). The next step consumes this file.

### 5.4 Build the scalp feature bundle
```
PYTHON scripts/build_features.py --data-dir <DATA_NIX> --metadata outputs/trial_metadata.csv --montage outputs/montage_intersection.json --out-dir outputs/features
```
Windows the maintenance period, extracts per-band power and channel-covariance features on the
common montage, and writes `outputs/features/feature_bundle.npz` (+ feature metadata and an
`exclusions.csv` naming every dropped trial/channel — no silent exclusions).

### 5.5 Define leave-one-subject-out folds
```
PYTHON scripts/make_loso_splits.py --bundle outputs/features/feature_bundle.npz --out-dir outputs/features
```
Writes `outputs/features/loso_folds.json`. All model selection happens inside training subjects
only; each held-out subject is touched once, for scoring.

### 5.6 Run the model ladder (the signal decoders)

**Rung 1 — regularized linear (headline linear model):**
```
PYTHON scripts/run_load_decoder.py --bundle outputs/features/feature_bundle.npz --model logistic --feature-family all --channel-set all --out-dir outputs/decoding
```
Produces `predictions_logistic_all_all.csv`, `subject_scores_logistic_all_all.csv`,
`summary_logistic_all_all.json`. (Rerun with `--feature-family band_power` / `covariance`, with
`--model lda`, and with `--channel-set brain` to reproduce the other rung-1 diagnostics whose
files appear in `outputs/decoding/`.)

**Rungs 2–3 — Riemannian (filter-bank covariance tangent space + minimum-distance-to-mean):**
```
PYTHON scripts/run_riemann_decoder.py --bundle outputs/features/feature_bundle.npz --method tangent --channel-set all --out-dir outputs/decoding
PYTHON scripts/run_riemann_decoder.py --bundle outputs/features/feature_bundle.npz --method mdm --channel-set all --out-dir outputs/decoding
```
(Add `--recenter` to reproduce the subject-recentered `*rc*` variants.)

**Rung 4 — EEGNet (the strongest model; the headline mechanism analysis is built on this):**
```
PYTHON scripts/run_eegnet_decoder.py --data-dir <DATA_NIX> --bundle outputs/features/feature_bundle.npz --channel-set all --out-dir outputs/decoding
```
Produces `predictions_eegnet_raw_all.csv`, `subject_scores_eegnet_raw_all.csv`,
`summary_eegnet_raw_all.json`. The script gradient-checks its own backprop before training and
prints the per-fold progress. This is the slowest step. (Rerun with `--channel-set brain` for the
6-channel brain-only reference check that rules out a reference-channel artifact.)

### 5.7 Non-signal controls
```
PYTHON scripts/run_control_models.py --bundle outputs/features/feature_bundle.npz --metadata outputs/features/feature_metadata.csv --signal-predictions outputs/decoding/predictions_eegnet_raw_all.csv --signal-subject-scores outputs/decoding/subject_scores_eegnet_raw_all.csv --out-dir outputs/controls
```
Runs the pre-declared controls — within-fold **label-shuffle** (null), **behavioral-only**
(non-signal task covariates, *excluding* set size and anything that encodes it), and
**timing-only** — on the same folds, and records the strongest control per subject. Writes
`control_*_eegnet_raw_all.*`. (Repeat with the `logistic_all_all` and `tangent_cov_all`
prediction files to reproduce their control sets.)

```
PYTHON scripts/run_behavioral_control_ablation.py --bundle outputs/features/feature_bundle.npz --metadata outputs/features/feature_metadata.csv --out-dir outputs/controls
```
Ablates the behavioral-only control to show *which* covariate carries it (the pre-declared
`previous_trial_correct` task-schedule channel). Writes `behavioral_ablation_*`.

### 5.8 Subject-level statistics and the success gate
```
PYTHON scripts/summarize_subject_statistics.py --control-subject-scores outputs/controls/control_subject_scores_eegnet_raw_all.csv --out-dir outputs/statistics --tag eegnet_raw_all
```
Applies the **pre-declared success thresholds** (defaults: improvement ≥ 0.075, ≥ 7/9 subjects
positive, leave-one-out mean ≥ 0.04) and computes the subject-level sign-flip interval and
bootstrap CI. Writes `outputs/statistics/summary_eegnet_raw_all.json` (and `.md`,
`subject_statistics_eegnet_raw_all.csv`). Run again with the `logistic_all_all` control scores
for the linear model's statistics.

### 5.9 Mechanism layer (Part B)
```
PYTHON scripts/audit_mtl_coverage.py --data-dir <DATA_NIX> --out-dir outputs/mechanism
PYTHON scripts/run_mtl_bandpower_probe.py --data-dir <DATA_NIX> --bundle outputs/features/feature_bundle.npz --signal-predictions outputs/decoding/predictions_eegnet_raw_all.csv --out-dir outputs/mechanism --tag eegnet_raw_all
PYTHON scripts/run_mtl_residual_coupling_probe.py --trial-summary outputs/mechanism/mtl_bandpower_trial_summary_eegnet_raw_all.csv --metadata outputs/trial_metadata.csv --out-dir outputs/mechanism --tag eegnet_raw_all
PYTHON scripts/run_mtl_confirmatory_coupling_gate.py --residual-summary outputs/mechanism/mtl_residual_coupling_summary_eegnet_raw_all.json --subject-summary outputs/mechanism/mtl_residual_coupling_subject_summary_eegnet_raw_all.csv --out-dir outputs/mechanism --tag eegnet_raw_all
```
First audits per-subject MTL electrode coverage (all 9 subjects qualify — ≥ 2 contacts in
amygdala/hippocampus). Then measures intracranial MTL theta/alpha band power against load and
against the decoder's scores; residualizes that coupling against load, the task schedule, and
behavior; and finally evaluates the **fixed, pre-registered Part B confirmatory gate**. The gate
output records that it is **not met** — Part B stays exploratory.

### 5.10 Compile the amendment evidence summary
```
PYTHON scripts/summarize_phase2_amendment_evidence.py --statistics-summary outputs/statistics/summary_eegnet_raw_all.json --behavioral-ablation-summary outputs/controls/behavioral_ablation_summary.json --bandpower-summary outputs/mechanism/mtl_bandpower_summary_eegnet_raw_all.json --residual-summary outputs/mechanism/mtl_residual_coupling_summary_eegnet_raw_all.json --out-dir outputs/amendment --tag eegnet_raw_all
```
Collates the load-bearing numbers into a single `outputs/amendment/phase2_amendment_evidence_eegnet_raw_all.{json,md}`.

### 5.11 Render the verification dashboard (regenerates the file from Section 1)
```
PYTHON scripts/render_verification_dashboard.py --predictions outputs/controls/control_predictions_eegnet_raw_all.csv --subject-statistics outputs/statistics/subject_statistics_eegnet_raw_all.csv --summary outputs/statistics/summary_eegnet_raw_all.json --mechanism-gate outputs/mechanism/mtl_confirmatory_coupling_gate_eegnet_raw_all.json --mechanism-subject-summary outputs/mechanism/mtl_residual_coupling_subject_summary_eegnet_raw_all.csv --out-dir outputs/dashboard
```
Writes `outputs/dashboard/verification_dashboard_eegnet_raw_all.html` — the same dashboard
shipped in this packet. Open it and confirm it matches.

---

## 6. What you should see (expected results)

If reproduction succeeded, the headline EEGNet statistics
(`outputs/statistics/summary_eegnet_raw_all.json`) match these values:

| Quantity | Expected | Pre-declared bar | Pass? |
|---|---|---|---|
| Mean decoder balanced accuracy | **0.616** | — (chance 0.50) | — |
| Mean strongest-control balanced accuracy | **0.593** | — | — |
| Mean improvement over strongest control | **+0.023** | ≥ +0.075 | ✗ |
| Subjects above strongest control | **5 / 9** | ≥ 7 / 9 | ✗ |
| Min leave-one-out mean improvement | **−0.001** (removing S04) | ≥ +0.04 | ✗ |
| Subject sign-flip p (two-sided) | **0.523** | — | — |
| Bootstrap 95% CI of mean improvement | **[−0.022, +0.081]** | must exclude 0 | ✗ (crosses 0) |
| **Headline success** | **`false`** | | **bounded negative** |

The single-subject dependence is the key diagnostic: the mean improvement is positive only
because of subject **S04** (its leave-one-out mean of −0.001 is the only non-positive row).

The simpler models score below the strong behavioral shortcut entirely — the headline linear
model (`summary_logistic_all_all.json`) has a mean improvement of **−0.033** (3/9 subjects
above control). EEGNet is the *only* rung above the strongest control on the mean, and it still
fails the bar.

Part B confirmatory gate (`outputs/mechanism/mtl_confirmatory_coupling_gate_eegnet_raw_all.json`):

| Coupling metric | Mean | Positive subjects | Sign-flip p (2-sided) |
|---|---|---|---|
| Raw | +0.068 | 7 / 9 | 0.051 |
| Load-residualized | +0.050 | 5 / 9 | 0.133 |
| **Schedule-residualized (the fixed gate metric)** | **+0.011** | **4 / 9** | **0.746** |
| Behavior-residualized | +0.013 | 5 / 9 | 0.715 |

`gate_passed: false`. The raw coupling is suggestive but does not survive residualization; Part B
is an exploratory lead, not a validated deep-source readout.

> Small numeric differences (last decimal place) across platforms or BLAS builds are normal and
> do not change any pass/fail verdict. The verdicts above are robust to that level of noise.

---

## 7. Why a clean negative is a real result

The study was designed so the answer would be trustworthy in either direction. The controls and
the success thresholds were written down **before any model was run**. The hardest control —
behavioral-only — is strong precisely because the task's design leaks information: in this
dataset an incorrect trial forces the *next* trial to a specific set size, so
`previous_trial_correct` predicts load well on its own. A decoder only earns credit for reading
the *brain* if it beats that shortcut, and under leave-one-subject-out evaluation none of the
models did by the required margin. That is a bounded, reusable fact for the larger
"affordable deep-brain readout from cheap EEG" research program: the wall, for this dataset, is
the 8-channel common montage combined with cross-subject transfer — not the choice of model. The
full reasoning is in the Technical Report and the Accessible Piece alongside this packet.

---

## 8. Licensing and attribution

- **This packet's code** (everything in `scripts/`, `utils/`, and this packet) is released under
  the **MIT License** — see [`LICENSE`](LICENSE). Permissive; commercial use allowed.
- **The dataset** is **CC BY-SA 4.0**. **The raw recordings are not redistributed here** —
  you download them yourself from the G-Node DOI (Section 2). **A derived extract of them is
  redistributed here:** `verification_dashboard.html` embeds **1,683 trial-level records**
  — subject, session and trial identifiers, the ground-truth label, the set size, and the
  model and control outputs for each trial. That data layer carries the dataset's own
  CC BY-SA 4.0 terms: if you reuse it, attribute the dataset authors as cited below and
  observe those terms. Dandelion's markup and expression around it are MIT. If you
  redistribute the data or an adaptation of it, you must attribute the original authors and
  share under a compatible license. Any derived figure or table that travels outside this
  repository should carry dataset attribution.
- **Dependencies** all carry licenses that permit commercial use: NumPy, SciPy, h5py, nixio,
  pandas, scikit-learn (BSD-family); matplotlib (PSF, BSD-compatible); pyarrow (Apache-2.0).
  Exact pinned versions are in [`requirements.txt`](requirements.txt).

### How to cite the dataset

> Boran, E., Fedele, T., Steiner, A., Hilfiker, P., Stieglitz, L., Grunwald, T., Sarnthein, J.
> (2019). *Dataset of simultaneous scalp EEG and intracranial EEG recordings and human medial
> temporal lobe units during a verbal working memory task.* G-Node.
> https://doi.org/10.12751/g-node.d76994 — licensed **CC BY-SA 4.0**:
> https://creativecommons.org/licenses/by-sa/4.0/
>
> The descriptor paper is a separate work, with its own title, year and license:
> Boran, E., Fedele, T., Steiner, A., Hilfiker, P., Stieglitz, L., Grunwald, T., Sarnthein, J.
> (2020). *Dataset of human medial temporal lobe neurons, scalp and intracranial EEG during a
> verbal working memory task.* Scientific Data **7**, 30.
> https://doi.org/10.1038/s41597-020-0364-3 (CC BY 4.0).

---

## 9. Scope and limitations

This is a measurement study on **9 subjects**, not a clinical or diagnostic tool, and it makes no
medical claims. The dominant limitation is the sample size: with 9 subjects, the dataset cannot
disambiguate a real load-linked shared MTL state from a schedule-linked correlate, which is
exactly why Part B is reported as exploratory. The contribution is an honest, fully reproducible
characterization of a first rung: a bounded negative for transferable load decoding from an
8-channel common montage, plus a named next signal to test with a better-powered dataset.
