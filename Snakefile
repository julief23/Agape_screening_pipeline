from pathlib import Path

wildcard_constraints:
    chunk = r"\d{4}"


rule all:
    input:
        "results/AGAPE_pubchem_all_predictions.csv",
        "results/AGAPE_pubchem_highconfidence_active.csv",
        "results/AGAPE_pubchem_highconfidence_inactive.csv"


rule fetch_pubchem:
    output:
        "data/raw/CID-SMILES.gz"
    log:
        "logs/fetch_pubchem.log"
    shell:
        """
        mkdir -p logs data/raw
        python workflow/scripts/fetch_pubchem.py > {log} 2>&1
        """


checkpoint split_pubchem:
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


def get_chunks(wildcards):
    ckpt = checkpoints.split_pubchem.get(**wildcards)
    chunk_dir = Path(ckpt.output[0])

    chunks = sorted(
        int(p.stem.replace("chunk_", ""))
        for p in chunk_dir.glob("chunk_*.csv")
    )

    return [f"{c:04d}" for c in chunks]


def get_prediction_files(wildcards):
    return expand(
        "data/predictions/pred_{chunk}.csv",
        chunk=get_chunks(wildcards)
    )


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


rule merge_predictions:
    input:
        get_prediction_files
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