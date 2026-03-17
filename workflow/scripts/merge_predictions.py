import pandas as pd
from pathlib import Path

input_files = snakemake.input
output_all = Path(snakemake.output.all)
output_active = Path(snakemake.output.active)
output_inactive = Path(snakemake.output.inactive)

dfs = []

for f in input_files:
    dfs.append(pd.read_csv(f))

full_df = pd.concat(dfs, ignore_index=True)

# Save full prediction table
full_df.to_csv(output_all, index=False)

# High-confidence subsets
high = full_df[full_df["confidence_level"] == "High"]

high_active = high[high["prediction"] == "ACTIVE"]
high_inactive = high[high["prediction"] == "INACTIVE"]

high_active.to_csv(output_active, index=False)
high_inactive.to_csv(output_inactive, index=False)

print("Total molecules:", len(full_df))
print("High-confidence ACTIVE:", len(high_active))
print("High-confidence INACTIVE:", len(high_inactive))