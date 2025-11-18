# models/predict.py  (manual tester)
import pandas as pd
import joblib
import os
import sys

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
    return {"prediction": int(pred), "fraud_probability": float(prob)}

def get_user_input():
    print("\nEnter transaction details (leave transaction_id blank to auto-assign):")
    txn_id_raw = input("Transaction ID (press Enter to let DB auto-assign): ").strip()
    txn_id = int(txn_id_raw) if txn_id_raw else None
    return {
        "transaction_id": txn_id,
        "amount": float(input("Amount: ")),
        "timestamp": input("Timestamp (YYYY-MM-DD HH:MM:SS): "),
        "location": input("Location: "),
        "merchant": input("Merchant: "),
        "category": input("Category: "),
        "transaction_type": input("Transaction Type (online/offline/international): "),
        "device_id": int(input("Device ID: ")),
        "user_id": int(input("User ID: "))
    }

if __name__ == "__main__":
    print("Choose mode: [1] Manual [2] Default example")
    ch = input("Choice (1/2): ").strip()
    if ch == "1":
        data = get_user_input()
    else:
        data = {
            "transaction_id": None,
            "amount": 95000,
            "timestamp": "2024-12-25 02:45:10",
            "location": "Russia",
            "merchant": "Unknown",
            "category": "crypto",
            "transaction_type": "international",
            "device_id": 999,
            "user_id": 45
        }
        print("\nUsing default example:", data)

    res = predict_transaction(data)
    print("Prediction:", res)
    data_to_save = data.copy()
    data_to_save["label"] = "fraud" if res["prediction"] == 1 else "legit"
    data_to_save["fraud_probability"] = res["fraud_probability"]
    ok = save_alert(data_to_save)
    print("Saved to DB:", ok)
