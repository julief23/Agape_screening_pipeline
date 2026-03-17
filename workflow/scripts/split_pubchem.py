import pandas as pd
from pathlib import Path

INPUT_FILE = Path("data/raw/CID-SMILES.gz")
OUTPUT_DIR = Path("data/chunks")
CHUNK_SIZE = 10000

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

reader = pd.read_csv(
    INPUT_FILE,
    sep="\t",
    compression="gzip",
    names=["CID", "SMILES"],
    chunksize=CHUNK_SIZE
)

for i, chunk in enumerate(reader, start=1):
    chunk_id = f"{i:04d}"
    out_file = OUTPUT_DIR / f"chunk_{chunk_id}.csv"
    chunk.to_csv(out_file, index=False)
    print(f"[SPLIT] Saved {out_file}")

print("--------------------------------")
print("Split completed successfully.")
print("--------------------------------")