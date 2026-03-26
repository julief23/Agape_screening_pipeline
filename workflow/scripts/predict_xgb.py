import pandas as pd
import pickle


def load_model(model_file):
    with open(model_file, "rb") as f:
        return pickle.load(f)


def predict(model, df):
    """
    Input: df with metadata + scaled features
    Output: result dataframe
    """

    meta_cols = ["CID", "SMILES", "canonical_smiles"]
    X = df.drop(columns=meta_cols)

    probs = model.predict_proba(X)[:, 1]
    preds = (probs > 0.5).astype(int)

    confidence = [max(p, 1 - p) for p in probs]

    confidence_level = [
        "High" if c > 0.85 else "Moderate" if c > 0.65 else "Low"
        for c in confidence
    ]

    result = df[meta_cols].copy()

    result["probability_active"] = probs
    result["prediction"] = ["ACTIVE" if p == 1 else "INACTIVE" for p in preds]
    result["model_confidence"] = confidence
    result["confidence_level"] = confidence_level

    print(f"[PREDICT] Rows: {len(result)}")

    return result