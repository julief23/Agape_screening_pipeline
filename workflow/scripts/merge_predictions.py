import pandas as pd
from pathlib import Path

input_files = list(snakemake.input)

output_all = Path(snakemake.output.all)
output_active = Path(snakemake.output.active)
output_inactive = Path(snakemake.output.inactive)

output_all.parent.mkdir(parents=True, exist_ok=True)
output_active.parent.mkdir(parents=True, exist_ok=True)
output_inactive.parent.mkdir(parents=True, exist_ok=True)

dfs = []

for f in input_files:
    path = Path(f)
    if path.exists() and path.stat().st_size > 0:
        dfs.append(pd.read_csv(path))

if not dfs:
    raise ValueError("No prediction files were found for merging.")

full_df = pd.concat(dfs, ignore_index=True)

full_df.to_csv(output_all, index=False)

high = full_df[full_df["confidence_level"] == "High"]

high_active = high[high["prediction"] == "ACTIVE"]
high_inactive = high[high["prediction"] == "INACTIVE"]

high_active.to_csv(output_active, index=False)
high_inactive.to_csv(output_inactive, index=False)

print("Total molecules:", len(full_df))
print("High-confidence ACTIVE:", len(high_active))
print("High-confidence INACTIVE:", len(high_inactive))