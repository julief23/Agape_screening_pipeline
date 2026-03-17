import pandas as pd
from pathlib import Path

# --------------------------------------
# Read chunk list generated earlier
# --------------------------------------

chunk_file = Path(snakemake.input.chunk_list)

with open(chunk_file) as f:
    chunks = [line.strip() for line in f if line.strip()]

# --------------------------------------
# Locate prediction files
# --------------------------------------

pred_files = [Path(f"data/predictions/pred_{c}.csv") for c in chunks]

dfs = []

for f in pred_files:
    if f.exists():
        dfs.append(pd.read_csv(f))

if not dfs:
    raise ValueError("No prediction files found to merge.")

# --------------------------------------
# Merge predictions
# --------------------------------------

full_df = pd.concat(dfs, ignore_index=True)

output_all = Path(snakemake.output.all)
output_active = Path(snakemake.output.active)
output_inactive = Path(snakemake.output.inactive)

# Save full results
full_df.to_csv(output_all, index=False)

# --------------------------------------
# High-confidence filtering
# --------------------------------------

high = full_df[full_df["confidence_level"] == "High"]

high_active = high[high["prediction"] == "ACTIVE"]
high_inactive = high[high["prediction"] == "INACTIVE"]

high_active.to_csv(output_active, index=False)
high_inactive.to_csv(output_inactive, index=False)

# --------------------------------------
# Reporting
# --------------------------------------

print("Total molecules:", len(full_df))
print("High-confidence ACTIVE:", len(high_active))
print("High-confidence INACTIVE:", len(high_inactive))