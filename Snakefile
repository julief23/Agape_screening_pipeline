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


rule stream_process_pubchem:
    input:
        "data/raw/CID-SMILES.gz"
    output:
        all="results/AGAPE_pubchem_all_predictions.csv",
        active="results/AGAPE_pubchem_highconfidence_active.csv",
        inactive="results/AGAPE_pubchem_highconfidence_inactive.csv"
    log:
        "logs/stream_pipeline.log"
    conda:
        "workflow/envs/full_pipeline.yaml"
    script:
        "workflow/scripts/stream_pipeline.py"