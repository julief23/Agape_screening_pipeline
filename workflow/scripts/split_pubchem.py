import pandas as pd
from pathlib import Path

# -----------------------------
# Paths
# -----------------------------

INPUT_FILE = Path("data/raw/CID-SMILES.gz")
OUTPUT_DIR = Path("data/chunks")
CHUNK_LIST_FILE = OUTPUT_DIR / "chunk_list.txt"

CHUNK_SIZE = 10000

# -----------------------------
# Ensure directories exist
# -----------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Read PubChem file in chunks
# -----------------------------

reader = pd.read_csv(
    INPUT_FILE,
    sep="\t",
    compression="gzip",
    names=["CID", "SMILES"],
    chunksize=CHUNK_SIZE
)

chunk_ids = []

# -----------------------------
# Split dataset
# -----------------------------

for i, chunk in enumerate(reader, start=1):

    chunk_id = f"{i:04d}"
    out_file = OUTPUT_DIR / f"chunk_{chunk_id}.csv"

    chunk.to_csv(out_file, index=False)

    chunk_ids.append(chunk_id)

    print(f"[SPLIT] Saved {out_file}")

# -----------------------------
# Write chunk list for Snakemake
# -----------------------------

with open(CHUNK_LIST_FILE, "w") as f:
    for cid in chunk_ids:
        f.write(cid + "\n")

print("\n--------------------------------")
print(f"Total chunks created: {len(chunk_ids)}")
print(f"Chunk list written to: {CHUNK_LIST_FILE}")
print("--------------------------------")