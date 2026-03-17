import pandas as pd
from rdkit import Chem
from pathlib import Path
import sys

input_file = Path(snakemake.input[0])
output_file = Path(snakemake.output[0])

df = pd.read_csv(input_file)

valid_rows = []

for _, row in df.iterrows():

    cid = row["CID"]
    smiles = row["SMILES"]

    mol = Chem.MolFromSmiles(smiles)

    if mol is None:
        continue

    canonical_smiles = Chem.MolToSmiles(mol, canonical=True)

    valid_rows.append({
        "CID": cid,
        "SMILES": smiles,
        "canonical_smiles": canonical_smiles
    })

clean_df = pd.DataFrame(valid_rows)

clean_df.to_csv(output_file, index=False)

print(f"Saved {len(clean_df)} valid molecules")