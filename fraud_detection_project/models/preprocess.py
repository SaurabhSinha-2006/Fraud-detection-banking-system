import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import hashlib

def hash_id(value):
    return int(hashlib.sha256(value.encode()).hexdigest(), 16) % (10**8)

def preprocess(df, training=False):
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Feature engineering
    df["hour"] = df["timestamp"].dt.hour
    df["day"] = df["timestamp"].dt.day
    df["amount_log"] = np.log1p(df["amount"])

    # Encoders
    le_type = LabelEncoder()
    le_loc = LabelEncoder()

    df["transaction_type_encoded"] = le_type.fit_transform(df["transaction_type"])
    df["location_encoded"] = le_loc.fit_transform(df["location"])

    # IMPORTANT FIX:
    # use hashed values but KEEP ORIGINAL COLUMN NAMES
    df["device_id"] = df["device_id"].astype(str).apply(hash_id)
    df["user_id"]   = df["user_id"].astype(str).apply(hash_id)

    # temporary fraud label for training
    if training:
        df["label"] = (
            (df["amount"] > 40000) |
            (df["hour"] > 22) |
            (df["hour"] < 5)
        ).astype(int)

    # FINAL features expected by model
    feature_cols = [
        "amount_log",
        "hour",
        "day",
        "transaction_type_encoded",
        "location_encoded",
        "device_id",
        "user_id",
    ]

    if training:
        feature_cols.append("label")

    return df[feature_cols]
