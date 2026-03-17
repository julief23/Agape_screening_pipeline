# AGAPE PubChem Screening Pipeline

Large-scale virtual screening pipeline for identifying potential **G-quadruplex stabilizing ligands** in the PubChem database using the **AGAPE machine learning model**.

This workflow processes large molecular datasets from PubChem, computes molecular descriptors, applies preprocessing identical to the AGAPE model training pipeline, and predicts ligand activity using a trained **XGBoost classifier**.

The pipeline is implemented with **Snakemake**, ensuring reproducibility, scalability, and automated environment management.

---

# Overview

The goal of this workflow is to enable **high-throughput in-silico screening of small molecules** to prioritize candidates likely to stabilize **G-quadruplex DNA structures**, which play important regulatory roles in genomic regions associated with cancer and other diseases.

The pipeline performs:

1. Retrieval of the PubChem **CID–SMILES dataset**
2. Dataset chunking for large-scale processing
3. SMILES validation and canonicalization
4. Molecular descriptor computation using **Mordred**
5. Feature alignment with the trained AGAPE model
6. Missing value imputation and feature scaling
7. Activity prediction using **XGBoost**
8. Confidence filtering of predictions
9. Merging of screening results

The pipeline is designed for **large datasets (millions of molecules)** and supports parallel execution.

---

# Workflow
PubChem CID–SMILES
│
▼
Download dataset
│
▼
Split dataset into chunks
│
▼
SMILES cleaning and validation
│
▼
Mordred descriptor computation
│
▼
Feature alignment with trained model
│
▼
Imputation + scaling
│
▼
XGBoost prediction
│
▼
Confidence filtering
│
▼
Merge results


---

# Pipeline structure


agape_screening_pipeline
│
├── Snakefile
├── README.md
│
├── workflow
│ ├── scripts
│ │ ├── fetch_pubchem.py
│ │ ├── split_pubchem.py
│ │ ├── clean_smiles.py
│ │ ├── compute_mordred_selected.py
│ │ ├── align_impute_scale_ml.py
│ │ ├── predict_xgb.py
│ │ └── merge_predictions.py
│ │
│ └── envs
│ ├── rdkit.yaml
│ ├── mordred.yaml
│ └── model_ml.yaml
│
├── models
│ ├── xgb_final_model.pkl
│ ├── xgb_feature_list.pkl
│ ├── xgb_final_scaler.pkl
│ └── xgb_final_imputer.pkl
│
├── data
│ ├── raw
│ ├── chunks
│ ├── processed
│ ├── descriptors
│ └── predictions
│
├── results
└── logs


The directories `data/`, `results/`, and `logs/` are created automatically by the workflow.

---

# Requirements

The pipeline requires:

- Python
- Snakemake
- Conda or Mamba
- RDKit
- Mordred
- scikit-learn
- XGBoost
- pandas
- NumPy

All dependencies are automatically installed through **Snakemake conda environments**.

---

# Installation

Clone the repository:

```bash
git clone https://github.com/julief23/agape_screening_pipeline.git
cd agape_screening_pipeline


conda create -n snakemake_env -c conda-forge -c bioconda snakemake
conda activate snakemake_env
---

# Running the pipeline

Run the full screening workflow with:

```bash
snakemake --cores 8 --use-conda
