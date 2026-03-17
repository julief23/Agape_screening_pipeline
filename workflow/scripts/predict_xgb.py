import pandas as pd
import pickle
from pathlib import Path

input_file = Path(snakemake.input.data)
model_file = Path(snakemake.input.model)

full_output = Path(snakemake.output.full)
high_output = Path(snakemake.output.high)

df = pd.read_csv(input_file)

meta_cols = ["CID", "SMILES", "canonical_smiles"]

X = df.drop(columns=meta_cols)

# -----------------------
# Load model
# -----------------------

with open(model_file, "rb") as f:
    model = pickle.load(f)

# -----------------------
# Predictions
# -----------------------

probs = model.predict_proba(X)[:, 1]
preds = (probs > 0.5).astype(int)

# -----------------------
# Confidence calculation
# -----------------------

confidence = [max(p, 1 - p) for p in probs]

confidence_level = []
for c in confidence:
    if c > 0.85:
        confidence_level.append("High")
    elif c > 0.65:
        confidence_level.append("Moderate")
    else:
        confidence_level.append("Low")

# -----------------------
# Full results
# -----------------------

result = df[meta_cols].copy()

result["probability_active"] = probs
result["prediction"] = preds
result["prediction"] = result["prediction"].map({1: "ACTIVE", 0: "INACTIVE"})
result["model_confidence"] = confidence
result["confidence_level"] = confidence_level

result.to_csv(full_output, index=False)

# -----------------------
# High-confidence subset
# -----------------------

highconf = result[result["confidence_level"] == "High"]

highconf = highconf[[
    "CID",
    "SMILES",
    "prediction",
    "probability_active",
    "model_confidence"
]]

full_output.parent.mkdir(parents=True, exist_ok=True)
high_output.parent.mkdir(parents=True, exist_ok=True)

highconf.to_csv(high_output, index=False)

print("Total molecules:", len(result))
print("High-confidence hits:", len(highconf))