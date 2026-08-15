<div align="center">
  <img src="assets/banner.jpg" alt="Project AIMS — AI Against Modern Slavery" width="100%">

  <h1>Project AIMS — AI Against Modern Slavery</h1>

  <p><em>Open datasets, models, and frameworks for analysing corporate modern slavery statements at scale.</em></p>

  <p>
    <a href="https://mila.quebec/en/ai4humanity/applied-projects/ai-against-modern-slavery-aims"><img alt="Project site" src="https://img.shields.io/badge/Project-Website-1f6feb"></a>
    <a href="https://doi.org/10.6084/m9.figshare.28489340"><img alt="Dataset DOI" src="https://img.shields.io/badge/Dataset%20DOI-10.6084%2Fm9.figshare.28489340-orange"></a>
    <a href="https://huggingface.co/datasets/mila-ai4h/AIMS.au"><img alt="Hugging Face" src="https://img.shields.io/badge/%F0%9F%A4%97%20Dataset-AIMS.au-yellow"></a>
    <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/License-CC--BY--4.0%20%2F%20MIT-green"></a>
    <a href="CITATION.cff"><img alt="Citation" src="https://img.shields.io/badge/Cite-CITATION.cff-blueviolet"></a>
  </p>
</div>

> ### 📌 Using this work? You must cite it.
> Everything here is free to use, adapt, and build on under **[CC-BY-4.0](LICENSE)** (data, figures,
> docs) and **[MIT](code/LICENSE)** (code). Both licences carry one condition: **attribution**.
> Cite the paper you actually drew on — the BibTeX sits at the top of each
> [paper folder](#where-to-go) — and cite the dataset DOI
> [`10.6084/m9.figshare.28489340`](https://doi.org/10.6084/m9.figshare.28489340) if you use the data.
> [**Full citation guide ↓**](#-how-to-cite)

---

## What this project does

Modern slavery legislation in Australia, the UK, and Canada requires large organisations to publish
annual statements describing what they are doing about modern slavery risks in their operations and
supply chains. **Hundreds of thousands of statements** now sit across the three national registries. Reading
them, comparing them, and judging whether they actually meet the mandatory reporting criteria is
slow, expert-intensive work — so most statements are never meaningfully reviewed.

Project AIMS builds the open datasets, models, and tools that make that review tractable: expert
sentence-level annotations aligned to the **Australian Modern Slavery Act**, benchmarks for
evaluating language models on compliance assessment, and frameworks that keep a human reviewer in
the loop. The annotation scheme is Australian throughout — the UK and Canadian test sets are
annotated against the same AU MSA criteria so the three jurisdictions stay directly comparable.

A collaboration between **[Mila — Quebec AI Institute](https://mila.quebec/)** and **[Queensland
University of Technology](https://www.qut.edu.au/)**, with hackathon delivery by **[Fundación Pasos
Libres](https://fundacionpasoslibres.org/)**. Supported by the National Action Plan to Combat Modern
Slavery 2020–25 Grants Program, administered by the Attorney-General's Department of Australia.

> **Phase 1** analysed UK statements and lives at
> [mila-studios/ai4h_aims-uk](https://github.com/mila-studios/ai4h_aims-uk).
> This repository is **Phase 2** — Australia and cross-jurisdictional work.

---

## Where to go

Each output has its own folder with a full README, figures, and reproduction notes.

| | Output | What it is | Venue |
|---|---|---|---|
| 📊 | **[AIMS.au](papers/aims-au/)** | The core dataset — 5,731 Australian statements, 800k+ expert-labelled sentences | ICLR 2025 |
| 🔍 | **[AIMSCheck](papers/aimscheck/)** | Three-level framework for AI-assisted compliance review, plus the AIMS.uk and AIMS.ca datasets | ACL 2025 |
| 🪶 | **[AIMSDistill](papers/aimsdistill/)** | Four specialised teachers distilled into one 340M student that beats an ≈8B ensemble at ~8× the speed | ESWA 2026 |
| ❓ | **[AIMS-QA](papers/aimsqa/)** | Question-answering framework that assesses statements *beyond* minimum legal compliance | Data & Policy 2026 |
| 🏆 | **[AIMS Hackathon 2025](hackathon-2025/)** | Global innovation challenge — 227 participants, 38 countries, 51 teams, 23 final solutions | — |
| 💻 | **[`code/`](code/)** | Shared, reproducible experiment codebase used across the papers | — |

---

## 📦 Data and models — where everything lives

Two homes, on purpose. **Figshare** is the archival record of the data: a DOI, a fixed version
history, the thing you cite. **Hugging Face** is the working copy: loads straight into code with no
download step.

### 🇦🇺🇬🇧🇨🇦 Datasets

<table>
<tr>
<td width="50%" valign="top">

**📚 Figshare — cite this**

[![DOI](https://img.shields.io/badge/DOI-10.6084%2Fm9.figshare.28489340-orange?style=for-the-badge)](https://doi.org/10.6084/m9.figshare.28489340)

The complete, archived record — all three jurisdictions plus the annotation specifications.
**18.3 GB · CC-BY-4.0**

</td>
<td width="50%" valign="top">

**🤗 Hugging Face — load this**

[![HF](https://img.shields.io/badge/%F0%9F%A4%97-mila--ai4h%2FAIMS.au-yellow?style=for-the-badge)](https://huggingface.co/datasets/mila-ai4h/AIMS.au)

The annotated Australian subset, ready to stream.

```python
from datasets import load_dataset
ds = load_dataset("mila-ai4h/AIMS.au")
```

</td>
</tr>
</table>

What's inside the [Figshare record](https://doi.org/10.6084/m9.figshare.28489340):

| File | Jurisdiction | Size |
|---|---|---:|
| `statements.full.20231129.deeplake.zip` — full corpus, DeepLake format | 🇦🇺 Australia | 18.2 GB |
| `AIMS.au_annotated…csv` — annotated set, excl. test/validation | 🇦🇺 Australia | 76 MB |
| `test_uk.csv` — AIMS.uk test set | 🇬🇧 United Kingdom | 473 kB |
| `test_ca.csv` — AIMS.ca test set | 🇨🇦 Canada | 688 kB |
| `AIMS Annotations Specifications.pdf` — annotation guidelines | 🇦🇺 Australia | 19 MB |

The DOI always resolves to the latest version; append `.v2` to cite a specific one.

**Companion record — [statement metadata](https://doi.org/10.6084/m9.figshare.30096127)**
(`10.6084/m9.figshare.30096127`, 1.5 MB, CC-BY-4.0). Statement-level metadata for the annotated
AIMS.au set — join it to the sentence labels to analyse disclosure by sector, entity size, or
reporting year, as in [AIMSCheck](papers/aimscheck/).

> **All three datasets use the Australian MSA annotation scheme.** The UK and Canadian statements
> are annotated against AU MSA criteria rather than their own local wording, which is what makes
> cross-jurisdictional comparison valid. See the Annotation Specifications for the full scheme.

### 🧠 Model weights

| Model | Used by | Where |
|---|---|---|
| Llama 3.2 3B (+100-word context) | Best performer in [AIMS.au](papers/aims-au/) and [AIMSCheck](papers/aimscheck/) | [![Figshare](https://img.shields.io/badge/Figshare-weights-orange)](https://figshare.com/articles/dataset/LLAMA_context_100_weights/29174045?file=54904154) |
| ModernBERT distilled students — `au.pth`, `uk.pth`, `ca.pth` (1.47 GB each) | [AIMSDistill](papers/aimsdistill/) | [![Figshare](https://img.shields.io/badge/Figshare-DOI-orange)](https://doi.org/10.6084/m9.figshare.33261576) |
| AIMS-QA context classifier | [AIMS-QA](papers/aimsqa/) Agent 1 — this is the same `au.pth` file | [![Figshare](https://img.shields.io/badge/Figshare-DOI-orange)](https://doi.org/10.6084/m9.figshare.33261576) |
| Teacher-model logits | [AIMSDistill](papers/aimsdistill/) reproduction | [`logits.zip`](https://doi.org/10.6084/m9.figshare.33261576) — in the same record |
| AIMS-QA SentenceBERT retriever (87 MB) | [AIMS-QA](papers/aimsqa/) Agent 2 | [![Figshare](https://img.shields.io/badge/Figshare-DOI-orange)](https://doi.org/10.6084/m9.figshare.33261639) |

Model weights are too large for a git repository — GitHub's free Git LFS allowance is 1 GB total,
and a single student checkpoint is 1.47 GB. They are hosted externally instead, and the code
downloads what it needs.

## Prompts

All **40 experimental prompts** from [AIMS.au](papers/aims-au/) and [AIMSCheck](papers/aimscheck/)
are in [`prompts/`](prompts/) as plain text — one file per criterion per variant, so they can be
diffed, reviewed, and reused without opening a Word document.

| | Prompts | Variants |
|---|---|---|
| [`prompts/aims-au/`](prompts/aims-au/) | 22 | no-context · with-context (±100 words) |
| [`prompts/aimscheck/`](prompts/aimscheck/) | 18 | zero-shot CoT · few-shot CoT |

They encode the annotation guidelines in prose — reading the Approval prompt is the quickest way to
see why "considered by the board" doesn't satisfy the criterion. See
[`prompts/README.md`](prompts/README.md) for the full index.

---

## 🔁 Reproducibility

Every paper in this repository can be reproduced from what is public: the data (Figshare DOI),
the prompts (`prompts/`), the configs and code (`code/`, `papers/*/src/`), and the released
weights. Each paper folder has a **Reproduce** section with the exact commands.

| Output | Reproduce with | Code state used in the paper |
|---|---|---|
| [AIMS.au](papers/aims-au/#reproduce) | Hydra configs in [`code/`](code/) — `python train.py experiment=…` | release [`v1`](https://github.com/mila-studios/ai4h_aims-au/releases/tag/v1) |
| [AIMSCheck](papers/aimscheck/#reproduce) | same codebase + [`prompts/aimscheck/`](prompts/aimscheck/) + evidence-tracking notebooks | release [`v1`](https://github.com/mila-studios/ai4h_aims-au/releases/tag/v1) |
| [AIMSDistill](papers/aimsdistill/) | [`Duoyi1/AimsDistill-paper`](https://github.com/Duoyi1/AimsDistill-paper) + teacher logits + released students | that repository, `main` |
| [AIMS-QA](papers/aimsqa/#reproduce) | [`papers/aimsqa/src/`](papers/aimsqa/src/) runbook — `pipeline.py` | this repository |

Setup, common to everything driven from `code/`:

```bash
git clone https://github.com/mila-studios/ai4h_aims-au.git
cd ai4h_aims-au/code
conda create -n qut01 python=3.11 pip && conda activate qut01
pip install -r requirements.txt
cp .env.template .env   # set DATA_ROOT and OUTPUT_ROOT
```

Full framework documentation is in [`code/README.md`](code/README.md). If a reproduction fails,
[open an issue](https://github.com/mila-studios/ai4h_aims-au/issues) — failed replications are as
useful to us as successful ones.

---

## 📖 How to cite

**Citation is a licence condition, not a courtesy.** CC-BY-4.0 and MIT both permit reuse,
including commercially, on the condition that you give appropriate credit. Please cite the specific
output you used:

| If you used… | Cite |
|---|---|
| The dataset (any jurisdiction) | Figshare DOI [`10.6084/m9.figshare.28489340`](https://doi.org/10.6084/m9.figshare.28489340) **and** the AIMS.au paper |
| The AIMS.au benchmark or annotations | Bora et al., **ICLR 2025** → [BibTeX](papers/aims-au/#citation) |
| AIMS.uk / AIMS.ca, or the review framework | Bora et al., **ACL 2025** → [BibTeX](papers/aimscheck/#citation) |
| The distilled model or distillation method | Bora, Zhang et al., **ESWA 2026** → [BibTeX](papers/aimsdistill/#citation) |
| The question taxonomy or QA pipeline | Bora et al., **Data & Policy 2026** → [BibTeX](papers/aimsqa/#citation) |
| The repository as a whole | [`CITATION.cff`](CITATION.cff) — GitHub's **Cite this repository** button, sidebar |

Using several? Cite each one you relied on. If you're unsure which applies,
[ask](mailto:adrianaeufrosina.bora@connect.qut.edu.au) — we would rather help than be miscited.

### Attribution text

For non-academic reuse — dashboards, reports, tools, teaching material — include:

> Project AIMS (AI Against Modern Slavery) by Mila — Quebec AI Institute and Queensland University
> of Technology, licensed under CC-BY-4.0.
> https://github.com/mila-studios/ai4h_aims-au

### If you build on this

We'd genuinely like to know — [open an issue](https://github.com/mila-studios/ai4h_aims-au/issues) or
[email us](mailto:adrianaeufrosina.bora@connect.qut.edu.au). Downstream uses help make the case for
continued funding of open research infrastructure in this space.

## 🤝 Contributing

Corrections to annotations, new jurisdictions, evaluation code, and documentation improvements are
all welcome — [open an issue](https://github.com/mila-studios/ai4h_aims-au/issues) first for anything
beyond a typo. Two things to know: all three datasets are annotated against the **Australian MSA
criteria** (judge a label against those and the Annotation Specifications, not local UK/CA
wording), and please don't submit statement text from elsewhere or anything expanding personal
data beyond the public source documents. Contributions land under the repository licences below.

## 📄 License

| What | Licence | Means |
|---|---|---|
| Data, annotations, figures, documentation | **[CC-BY-4.0](LICENSE)** | Use, share, adapt, commercially — **with credit** |
| Code in [`code/`](code/) and paper `src/` folders | **[MIT](code/LICENSE)** | Use, modify, distribute, sell — just keep the copyright notice |

Both licences are permissive. Neither is public domain: **attribution is mandatory**, and stripping
it is a licence breach, not an oversight. See [How to cite](#-how-to-cite).

**Not covered by these licences:**

- The **source statements** themselves — Crown/corporate copyright, redistributed under the terms
  of the registries they came from.
- **Upstream models** (ModernBERT, Llama, Gemma, GPT) — each carries its own licence and
  acceptable-use policy, which you must comply with independently.
- **Hackathon team solutions** — licensed separately by their authors; see each repository.

**Responsible use.** These tools are decision-support for human reviewers, not automated compliance
verdicts. Every paper here states that misclassifying a corporate disclosure carries legal and
ethical consequences and that full automation is not recommended. Please don't publish automated
judgements about named companies without expert review.

## 📞 Contact

- **Project site:** [mila.quebec — AI Against Modern Slavery](https://mila.quebec/en/ai4humanity/applied-projects/ai-against-modern-slavery-aims)
- **Code or data questions:** [open an issue](https://github.com/mila-studios/ai4h_aims-au/issues/new/choose)
- **Contact:** Adriana Eufrosina Bora — [adrianaeufrosina.bora@connect.qut.edu.au](mailto:adrianaeufrosina.bora@connect.qut.edu.au)
