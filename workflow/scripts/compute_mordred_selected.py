import numpy as np

# numpy compatibility
if not hasattr(np, "float"):
    np.float = float
if not hasattr(np, "int"):
    np.int = int
if not hasattr(np, "bool"):
    np.bool = bool

import pandas as pd
from rdkit import Chem
from mordred import Calculator, descriptors
import pickle
import joblib


def compute_descriptors(df, feature_file):
    """
    Input: df with columns [CID, SMILES, canonical_smiles]
    Output: same + descriptors aligned to feature_list
    """

    # -----------------------------
    # Load feature list
    # -----------------------------
    if str(feature_file).endswith(".joblib"):
        feature_list = joblib.load(feature_file)
    else:
        with open(feature_file, "rb") as f:
            feature_list = pickle.load(f)

    feature_list = list(feature_list)

    # -----------------------------
    # Build calculator (selected only)
    # -----------------------------
    calc_full = Calculator(descriptors, ignore_3D=True)
    selected_descriptors = [
        d for d in calc_full.descriptors if str(d) in feature_list
    ]

    if not selected_descriptors:
        raise ValueError("No descriptors match feature list")

    calc = Calculator(selected_descriptors, ignore_3D=True)

    # -----------------------------
    # Compute descriptors safely
    # -----------------------------
    rows = []

    for _, row in df.iterrows():
        mol = Chem.MolFromSmiles(row["canonical_smiles"])
        if mol is None:
            continue

        try:
            desc = calc(mol)
        except:
            desc = [np.nan] * len(feature_list)

        rows.append(desc)

    desc_df = pd.DataFrame(rows, columns=feature_list)

    # -----------------------------
    # Align with metadata (NO LOSS)
    # -----------------------------
    meta_df = df.iloc[:len(desc_df)].reset_index(drop=True)

    final_df = pd.concat([meta_df, desc_df], axis=1)

    print(f"[MORDRED] Rows: {len(final_df)}")
    print(f"[MORDRED] Features: {len(feature_list)}")

    return final_df