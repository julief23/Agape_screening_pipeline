from glob import glob
import os

# --------------------------------------------------
# Detect all chunk IDs
# --------------------------------------------------

CHUNKS = [
    os.path.basename(f).replace("chunk_", "").replace(".csv", "")
    for f in glob("data/chunks/chunk_*.csv")
]

# --------------------------------------------------
# Final targets
# --------------------------------------------------

rule all:
    input:
        expand("data/predictions/pred_{chunk}.csv", chunk=CHUNKS),
        "results/AGAPE_pubchem_all_predictions.csv",
        "results/AGAPE_pubchem_highconfidence_active.csv",
        "results/AGAPE_pubchem_highconfidence_inactive.csv"


# --------------------------------------------------
# Step 1 — Download PubChem
# --------------------------------------------------

rule fetch_pubchem:
    output:
        "data/raw/CID-SMILES.gz"
    log:
        "logs/fetch_pubchem.log"
    shell:
        """
        python workflow/scripts/fetch_pubchem.py > {log} 2>&1
        """


# --------------------------------------------------
# Step 2 — Split PubChem into chunks
# --------------------------------------------------

rule split_pubchem:
    input:
        "data/raw/CID-SMILES.gz"
    output:
        directory("data/chunks")
    log:
        "logs/split_pubchem.log"
    conda:
        "workflow/envs/rdkit.yaml"
    script:
        "workflow/scripts/split_pubchem.py"


# --------------------------------------------------
# Step 3 — Clean SMILES
# --------------------------------------------------

rule clean_smiles:
    input:
        "data/chunks/chunk_{chunk}.csv"
    output:
        "data/processed/clean_{chunk}.csv"
    log:
        "logs/clean_{chunk}.log"
    conda:
        "workflow/envs/rdkit.yaml"
    script:
        "workflow/scripts/clean_smiles.py"


# --------------------------------------------------
# Step 4 — Compute Mordred descriptors
# --------------------------------------------------

rule compute_mordred_selected:
    input:
        chunk="data/processed/clean_{chunk}.csv",
        features="models/xgb_feature_list.pkl"
    output:
        "data/descriptors/desc_{chunk}.csv"
    log:
        "logs/mordred_{chunk}.log"
    conda:
        "workflow/envs/mordred.yaml"
    script:
        "workflow/scripts/compute_mordred_selected.py"


# --------------------------------------------------
# Step 5 — Align features, impute, scale
# --------------------------------------------------

rule align_impute_scale:
    input:
        desc="data/descriptors/desc_{chunk}.csv",
        features="models/xgb_feature_list.pkl",
        imputer="models/xgb_final_imputer.pkl",
        scaler="models/xgb_final_scaler.pkl"
    output:
        "data/processed/scaled_{chunk}.csv"
    log:
        "logs/preprocess_{chunk}.log"
    conda:
        "workflow/envs/model_ml.yaml"
    script:
        "workflow/scripts/align_impute_scale_ml.py"


# --------------------------------------------------
# Step 6 — Predict with XGBoost
# --------------------------------------------------

rule predict_xgb:
    input:
        data="data/processed/scaled_{chunk}.csv",
        model="models/xgb_final_model.pkl"
    output:
        full="data/predictions/pred_{chunk}.csv",
        high="data/predictions/highconf_{chunk}.csv"
    log:
        "logs/predict_{chunk}.log"
    conda:
        "workflow/envs/model_ml.yaml"
    script:
        "workflow/scripts/predict_xgb.py"


# --------------------------------------------------
# Step 7 — Merge all predictions
# --------------------------------------------------

rule merge_predictions:
    input:
        expand("data/predictions/pred_{chunk}.csv", chunk=CHUNKS)
    output:
        all="results/AGAPE_pubchem_all_predictions.csv",
        active="results/AGAPE_pubchem_highconfidence_active.csv",
        inactive="results/AGAPE_pubchem_highconfidence_inactive.csv"
    log:
        "logs/merge_predictions.log"
    conda:
        "workflow/envs/model_ml.yaml"
    script:
        "workflow/scripts/merge_predictions.py"