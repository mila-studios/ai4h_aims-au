<div align="center">

# Project AI Against Modern Slavery (AIMS)  Sandbox

[![PyTorch](https://img.shields.io/badge/PyTorch-ee4c2c?logo=pytorch&logoColor=white)](https://pytorch.org/get-started/locally/)
[![Lightning](https://img.shields.io/badge/-Lightning-792ee5?logo=pytorchlightning&logoColor=white)](https://lightning.ai/)
[![Hydra](https://img.shields.io/badge/Config-Hydra-89b8cd)](https://hydra.cc/)

</div>

## Description

A deep learning sandbox for Project AIMS.

This framework is primarily meant to help the prototyping of new models and data loaders. It relies
on [PyTorch](https://pytorch.org/get-started/locally/) in combination with
[Lightning](https://lightning.ai/), and is derived from the [Lightning-Hydra-Template
Project](https://github.com/ashleve/lightning-hydra-template).

The easiest way to use this framework is probably to clone it, add your own code inside its folder
structure, modify things as needed, and run your own experiments (derived from defaults/examples).
You can however also use it as a dependency if you are familiar with how Hydra configuration files
are handled.

## How to run an experiment

First, install the framework and its dependencies:

```bash
# clone project
git clone https://github.com/milatechtransfer/qut01-aims
cd qut01-aims

# create conda environment
conda create -n qut01 python=3.11 pip
conda activate qut01
pip install -r requirements.txt
```

Next, create a copy of the [`.env.template`](./.env.template) file, rename it to `.env`, and modify
its content so that at least all mandatory variables are filled. These include:

- `DATA_ROOT`: path to the root directory where all datasets are located. It will be internally
  used via Hydra/OmegaConf through the `utils.data_root_dir` config key. All datamodules that are
  implemented in the framework will likely define their root directory based on this location.

- `OUTPUT_ROOT`: path to the root directory where all outputs (logs, checkpoints, plots, ...) will
  be written. It will be internally used via Hydra/OmegaConf through the `utils.output_root_dir`
  config key. It is at that location where experiment and run directories will be created.
  

Note that this file is machine-specific, and it may contain secrets and API keys. Therefore, it will
always be ignored by version control (due to the `.gitignore` filters), and you should be careful
about logging its contents or printing it inside a script to avoid credential leaks.

Finally, launch an experiment using an existing config file, or create a new one:

```bash
python train.py experiment=example_mnist_classif
```

In this example, the `experiment=example_mnist_classif` argument tells Hydra to load a
configuration file named [`example_mnist_classif.yaml`](./qut01/configs/experiment/example_mnist_classif.yaml).
Note that since the entrypoint is Hydra-based, you can override any settings from the command line:

```bash
python train.py experiment=example_mnist_classif trainer.max_epochs=3
```

The experiment configuration files provide the main location from where settings should be modified
to run particular experiments. New experiments can be defined by copying and modifying existing
files. For more information on these files, see the [relevant section](#configuration-files).

## Framework Structure

This is a YAML-configuration-based Hydra project. Therefore, experiment configurations are defined
via a separate configuration file tree (see the next section for more information).

The rest of the framework can be defined as follows:

```
<repository_root>
  ├── data       => suggested root directory for datasets (might not exist); can be a symlink
  │   ├── <some_dataset_directory>
  │   ├── <some_other_dataset_directory>
  │   └── ...
  ├── logs       => suggested root directory for outputs (might not exist); can be a symlink
  │   ├── comet
  │   ├── tensorboard
  │   ├── ...
  │   └── runs
  │       └── <some_experiment_name>
  │           ├── <some_run_name>
  │           │   ├── ckpts
  │           │   └── ...
  │           └── <some_other_run_name>
  │               └── ...
  ├── notebooks  => contains notebooks used for data analysis, visualization, and demonstrations
  │   └── ...
  ├── qut01     => root directory for the framework's packages, configs, and modules
  │   ├── configs    => root directory for all configuration files; see next section
  │   │   └── ...
  │   ├── data       => contains subpackages related to data loading
  │   ├── metrics    => contains subpackages related to metrics/evaluation
  │   ├── models     => contains subpackages related to models/architectures
  │   └── utils      => generic utility module for the whole framework
  └── tests     => contains unit tests for qut01 framework packages/modules
      └── ...
```

The entrypoint scripts that can launch experiments (specified via an extra `experiment=...` CLI
argument) are:

- [`./train.py`](./train.py): used to launch model training experiments; will load the
  configuration file at [`qut01/configs/train.yaml`](./qut01/configs/train.yaml) by default
  before applying the experiment settings.
- [`./test.py`](./test.py): used to launch model testing experiments; will load the configuration
  file at [`qut01/configs/test.yaml`](./qut01/configs/test.yaml) by default before applying the
  experiment settings.
- [`./data_profiler.py`](./data_profiler.py): used to profile/debug data loading pipelines; will
  load the configuration file at [`qut01/configs/profiler.yaml`](./qut01/configs/profiler.yaml) by
  default before applying the experiment settings.
- [`./model_profiler.py`](./model_profiler.py): used to profile/debug model forward passes; will
  load the configuration file at [`qut01/configs/profiler.yaml`](./qut01/configs/profiler.yaml) by
  default before applying the experiment settings.

See the next section for information on the experiment configuration files and how to use them.

There are other data-related scripts that can be executed by themselves without involving Hydra
or experiment configuration files at all; these are:

- [`qut01/data/scripts/parse_raw_statements_data.py`](./qut01/data/scripts/parse_raw_statements_data.py):
  repackages statement data (text data extracted using ABBYY/fitz as well as PDF metadata) into a
  deeplake dataset.
- [`qut01/data/scripts/add_annotations_to_raw_dataset.py`](./qut01/data/scripts/add_annotations_to_raw_dataset.py):
  adds annotations provided via CSV files to the deeplake dataset created by the above script.
- [`qut01/data/scripts/check_annotation_overlap.py`](./qut01/data/scripts/check_annotation_overlap.py):
  analyzes an annotated deeplake dataset and computes its inter annotator agreement (IAA) metrics.
- [`qut01/data/scripts/annotation_validator.py`](./qut01/data/scripts/annotation_validator.py):
  allows the user to review and modify dataset annotations.

For info on how to use key components of this framework, refer to the demo notebooks in
[this folder](./notebooks).

## Configuration Files

When using Hydra, configuration files are used to provide and log settings across
the entire application. For a tutorial on Hydra, see the
[official documentation](https://hydra.cc/docs/tutorials/basic/your_first_app/simple_cli/).

In this framework, most of the already-existing configuration files provide default values for
settings across different categories. An experiment with a custom model, a custom dataset, custom
metrics, and/or other user-specified settings will likely rely on a new configuration file that
loads the default values and overrides some of them. Such experiment configuration files should be
placed in the `<repository_root>/qut01/configs/experiment/` directory.

Experiment configurations will typically override settings across the full scope of the
configuration tree, meaning that they will likely be defined with the `# @package _global_`
line. A good starting point on how to write such a configuration is to copy and modify one of the
examples, such as [this one](./qut01/configs/experiment/example_mnist_classif.yaml). This file can
be used to define overrides as well as new settings that may affect any aspect of an experiment
launched with the framework. Remember: to launch a training experiment for a file named
`some_new_experiment_config.yaml` in the `<repository_root>/qut01/configs/experiment/` directory,
you would run:

```bash
python train.py experiment=some_new_experiment_config
```

## Output files

The results of an experiment comes under the form of checkpoints, merged configuration files,
console logs, and any other artefact that your code may produce. By default, these will be saved
under the path defined by the `OUTPUT_ROOT` environment variable, under subdirectories named based
on experiment and run identifiers.

## Where to find the data

As of early 2024, the experiments are all based on data obtained by preprocessing the [Australian
Modern Slavery Register PDF statements](https://modernslaveryregister.gov.au/) using [ABBYY
FineReader](https://pdf.abbyy.com/) and [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/en/latest/)
to extract raw text. The annotations for the statements have been created by
[Tasq AI](https://www.tasq.ai/) and have been combined with the raw text data. The data repackaging
is done using the following scripts, which create a
[Deep Lake tensor dataset](https://docs.deeplake.ai/en/latest/Datasets.html):

```
  qut01/data/scripts/parse_raw_statements_data.py => repackages raw text into a deeplake dataset
  qut01/data/scripts/add_annotations_to_raw_dataset.py => adds annotations to the deeplake dataset
```

You can run these scripts using the raw data + annotation CSVs yourself to create your own
dataset, or download the already-generated dataset from the project's FigShare folder
[here](https://figshare.com/s/1b92ebfde3f2de2be0cf). As of
August 2024, the dataset is built using register statements downloaded on 2023-11-29, annotations
shipped by Tasq AI between 2024-01-15 and 2024-05-31, and validated annotations for 100 statements
created by the team. It can be downloaded from here:

Once generated (or downloaded and unzipped), the Deep Lake dataset (i.e. the folder which should be
named as `statements.20231129.deeplake`) should be located in the `DATA_ROOT` folder
specified as an environment variable. See the "How to run an experiment" section for more info.

To parse the resulting dataset, you can write your own code using the
[Deep Lake API](https://docs.deeplake.ai/en/latest/Datasets.html), or use the parser provided in
the framework at
[`qut01/data/dataset_parser.py`](./qut01/data/dataset_parser.py). See the
[`notebooks/data_parsing_demo.ipynb`](./notebooks/data_parsing_demo.ipynb) for a demo on how to
use it.

## Other Notes

For more info on the usage of the config files and hydra/Lightning tips+tricks, see the
[original template repository](https://github.com/ashleve/lightning-hydra-template) and the
[ssl4rs repository](https://github.com/plstcharles/ssl4rs).
