import pandas as pd
import numpy as np
import pickle
import joblib
from pathlib import Path

input_file = Path(snakemake.input.desc)
feature_file = Path(snakemake.input.features)
imputer_file = Path(snakemake.input.imputer)
scaler_file = Path(snakemake.input.scaler)

output_file = Path(snakemake.output[0])

df = pd.read_csv(input_file)

# -------------------------------------
# Load artifacts
# -------------------------------------

with open(feature_file, "rb") as f:
    feature_list = pickle.load(f)

imputer = joblib.load(imputer_file)
scaler = joblib.load(scaler_file)

feature_list = list(feature_list)

# -------------------------------------
# Extract descriptor matrix
# -------------------------------------

descriptor_df = df[feature_list].copy()

descriptor_df = descriptor_df.apply(pd.to_numeric, errors="coerce")
descriptor_df = descriptor_df.replace([np.inf, -np.inf], np.nan)

# -------------------------------------
# Impute
# -------------------------------------

X_imputed = imputer.transform(descriptor_df)

# -------------------------------------
# Scale
# -------------------------------------

X_scaled = scaler.transform(X_imputed)

X_scaled = pd.DataFrame(
    X_scaled,
    columns=feature_list,
    index=df.index
)

# -------------------------------------
# Merge metadata
# -------------------------------------

meta_cols = ["CID", "SMILES", "canonical_smiles"]

final_df = pd.concat([df[meta_cols], X_scaled], axis=1)

output_file.parent.mkdir(parents=True, exist_ok=True)
final_df.to_csv(output_file, index=False)

print("Rows:", len(final_df))
print("Features:", len(feature_list))
print("Saved:", output_file)