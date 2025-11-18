import pandas as pd
import joblib
import os
import sys

# FIX PATHS
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(BASE_DIR, "src"))

from preprocess import preprocess
from save_alert import save_alert

MODEL_PATH = os.path.join(BASE_DIR, "models", "fraud_model.pkl")
model = joblib.load(MODEL_PATH)

REQUIRED_FIELDS = [
    "amount",
    "timestamp",
    "location",
    "merchant",
    "category",
    "transaction_type",
    "device_id",
    "user_id"
]

def predict_transaction(data):
    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    df = pd.DataFrame([data])
    df_pre = preprocess(df, training=False)

    pred = model.predict(df_pre)[0]
    prob = model.predict_proba(df_pre)[0][1]

    return {
        "prediction": int(pred),
        "fraud_probability": float(prob)
    }


if __name__ == "__main__":

    default_input = {
        "transaction_id": 1009,
        "amount": 95000,
        "timestamp": "2024-12-25 02:45:10",
        "location": "Russia",
        "merchant": "Unknown",
        "category": "crypto",
        "transaction_type": "international",
        "device_id": 999,
        "user_id": 45
    }

    print("\nUsing default example:")
    print(default_input)

    result = predict_transaction(default_input)
    print("\nResult:")
    print(result)

    data_to_save = default_input.copy()
    data_to_save["label"] = "fraud" if result["prediction"] == 1 else "legit"
    data_to_save["fraud_probability"] = result["fraud_probability"]

    save_alert(data_to_save)

