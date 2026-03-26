import gzip
import os
import pandas as pd
import subprocess   # ✅ FIXED

from clean_smiles import clean_dataframe
from compute_mordred_selected import compute_descriptors
from align_impute_scale_ml import preprocess_features
from predict_xgb import predict, load_model


# -----------------------------
# Snakemake inputs
# -----------------------------
INPUT = snakemake.input[0]

FEATURE_FILE = "models/xgb_feature_list.pkl"
IMPUTER_FILE = "models/xgb_final_imputer.pkl"
SCALER_FILE = "models/xgb_final_scaler.pkl"
MODEL_FILE = "models/xgb_final_model.pkl"

OUT_ALL = snakemake.output.all
OUT_ACTIVE = snakemake.output.active
OUT_INACTIVE = snakemake.output.inactive

# Ensure output dirs exist
os.makedirs(os.path.dirname(OUT_ALL), exist_ok=True)

# -----------------------------
# Load model ONCE
# -----------------------------
model = load_model(MODEL_FILE)

# -----------------------------
# Parameters
# -----------------------------
BATCH_SIZE = 200

batch = []
processed = 0

# -----------------------------
# TOTAL SIZE (for progress %)
# -----------------------------
try:
    total_lines = int(subprocess.check_output(f"zcat {INPUT} | wc -l", shell=True))
    print(f"[INFO] Total molecules in file: {total_lines}")
except:
    total_lines = None


def flush_batch(batch, first_write):
    df = pd.DataFrame(batch, columns=["CID", "SMILES"])

    # CLEAN
    df = clean_dataframe(df)
    if df.empty:
        return 0

    # DESCRIPTORS
    desc = compute_descriptors(df, FEATURE_FILE)
    if desc.empty:
        return 0

    # PREPROCESS
    X = preprocess_features(
        desc,
        FEATURE_FILE,
        IMPUTER_FILE,
        SCALER_FILE
    )

    # PREDICT
    results = predict(model, X)

    # WRITE RESULTS
    results.to_csv(
        OUT_ALL,
        mode="a",
        header=first_write,
        index=False
    )

    # HIGH CONF
    high = results[results["model_confidence"] > 0.85]

    high_active = high[high["prediction"] == "ACTIVE"]
    high_inactive = high[high["prediction"] == "INACTIVE"]

    high_active.to_csv(
        OUT_ACTIVE,
        mode="a",
        header=first_write,
        index=False
    )

    high_inactive.to_csv(
        OUT_INACTIVE,
        mode="a",
        header=first_write,
        index=False
    )

    print(f"[BATCH] Processed batch of size {len(results)}")  # ✅ added

    return len(results)


# -----------------------------
# STREAM FILE
# -----------------------------
with gzip.open(INPUT, "rt") as f:
    first_write = True

    for line in f:
        try:
            cid, smiles = line.strip().split()
        except:
            continue

        batch.append((cid, smiles))

        if len(batch) == BATCH_SIZE:
            processed += flush_batch(batch, first_write)
            first_write = False
            batch = []

            # ✅ PROGRESS
            if total_lines:
                percent = (processed / total_lines) * 100
                print(f"[PROGRESS] {processed} molecules ({percent:.2f}%)")
            else:
                print(f"[PROGRESS] {processed} molecules")

            # ✅ CHECKPOINT
            if processed % 10000 == 0:
                if total_lines:
                    percent = (processed / total_lines) * 100
                    print(f"[CHECKPOINT] {processed} molecules processed ({percent:.2f}%)")
                else:
                    print(f"[CHECKPOINT] {processed} molecules processed")

    # last batch
    if batch:
        processed += flush_batch(batch, first_write)

print("DONE. Total processed:", processed)