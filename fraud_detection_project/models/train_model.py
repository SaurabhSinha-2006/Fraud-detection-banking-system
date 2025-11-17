import os
import joblib
from sklearn.ensemble import RandomForestClassifier

def train_model(df):
    # example model
    model = RandomForestClassifier()
    model.fit(df.drop("label", axis=1), df["label"])

    # save path = same folder as train_model.py
    folder = os.path.dirname(__file__)    # gives .../models
    save_path = os.path.join(folder, "fraud_model.pkl")

    joblib.dump(model, save_path)
    print("Model saved:", save_path)

