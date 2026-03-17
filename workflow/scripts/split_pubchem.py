import pandas as pd
from pathlib import Path

input_file = Path("data/raw/CID-SMILES.gz")
output_dir = Path("data/chunks")
chunk_list_file = output_dir / "chunk_list.txt"

chunk_size = 10000

output_dir.mkdir(parents=True, exist_ok=True)

reader = pd.read_csv(
    input_file,
    sep="\t",
    compression="gzip",
    names=["CID", "SMILES"],
    chunksize=chunk_size
)

chunk_ids = []

for i, chunk in enumerate(reader, start=1):

    chunk_id = f"{i:04d}"
    out_file = output_dir / f"chunk_{chunk_id}.csv"

    chunk.to_csv(out_file, index=False)

    chunk_ids.append(chunk_id)

    print(f"Saved {out_file}")

# write list of chunks for Snakemake
with open(chunk_list_file, "w") as f:
    for cid in chunk_ids:
        f.write(cid + "\n")

print(f"\nTotal chunks created: {len(chunk_ids)}")
print(f"Chunk list written to: {chunk_list_file}")