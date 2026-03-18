import pandas as pd
from rdkit import Chem
from pathlib import Path

input_file = Path(snakemake.input[0])
output_file = Path(snakemake.output[0])

# Ensure output directory exists
output_file.parent.mkdir(parents=True, exist_ok=True)

# Read chunk
df = pd.read_csv(input_file)

required_cols = {"CID", "SMILES"}
missing = required_cols - set(df.columns)
if missing:
    raise ValueError(f"Missing required columns in {input_file}: {missing}")

valid_rows = []

for _, row in df.iterrows():
    cid = row["CID"]
    smiles = str(row["SMILES"]).strip()

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

print(f"[CLEAN] Input file: {input_file}")
print(f"[CLEAN] Output file: {output_file}")
print(f"[CLEAN] Input rows: {len(df)}")
print(f"[CLEAN] Valid molecules: {len(clean_df)}")