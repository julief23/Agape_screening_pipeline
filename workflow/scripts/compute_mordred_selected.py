import numpy as np

# ---------------------------------
# numpy compatibility patch
# ---------------------------------
if not hasattr(np, "float"):
    np.float = float
if not hasattr(np, "int"):
    np.int = int
if not hasattr(np, "bool"):
    np.bool = bool

import pandas as pd
from rdkit import Chem
from mordred import Calculator, descriptors
from pathlib import Path
import pickle
import joblib


input_file = Path(snakemake.input[0])
feature_file = Path(snakemake.input[1])
output_file = Path(snakemake.output[0])

df = pd.read_csv(input_file)

# -----------------------------
# Load feature list
# -----------------------------
if feature_file.suffix == ".joblib":
    feature_list = joblib.load(feature_file)
else:
    with open(feature_file, "rb") as f:
        feature_list = pickle.load(f)

feature_list = list(feature_list)

# -----------------------------
# Build full Mordred calculator
# -----------------------------
calc = Calculator(descriptors, ignore_3D=True)

# Keep only descriptors present in the model feature list
selected_descriptors = [d for d in calc.descriptors if str(d) in feature_list]

if len(selected_descriptors) == 0:
    raise ValueError("No Mordred descriptors matched the XGBoost feature list.")

calc = Calculator(selected_descriptors, ignore_3D=True)

# -----------------------------
# Convert SMILES to molecules
# -----------------------------
mols = []
kept_rows = []

for _, row in df.iterrows():
    mol = Chem.MolFromSmiles(row["canonical_smiles"])
    if mol is None:
        continue
    mols.append(mol)
    kept_rows.append(row)

if len(mols) == 0:
    raise ValueError(f"No valid molecules found in {input_file}")

meta_df = pd.DataFrame(kept_rows).reset_index(drop=True)

# -----------------------------
# Compute descriptors
# -----------------------------
desc_df = calc.pandas(mols)

# Keep only the exact feature order expected by the model
desc_df = desc_df.reindex(columns=feature_list)

final_df = pd.concat([meta_df, desc_df], axis=1)
final_df.to_csv(output_file, index=False)

print(f"Input rows: {len(df)}")
print(f"Valid molecules: {len(mols)}")
print(f"Selected descriptors matched: {len(selected_descriptors)}")
print(f"Saved: {output_file}")