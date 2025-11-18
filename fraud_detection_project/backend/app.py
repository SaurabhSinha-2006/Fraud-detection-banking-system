# backend/app.py
import os, sys, json
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
from datetime import datetime
import mysql.connector

# --- make sure Flask can import your src modules and model ---
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
MODELS = os.path.join(ROOT, "models")
if SRC not in sys.path:
    sys.path.append(SRC)
if MODELS not in sys.path:
    sys.path.append(MODELS)

# import your existing utils
try:
    from preprocess import preprocess    # src/preprocess.py
    from save_alert import save_alert    # src/save_alert.py
except Exception as e:
    raise RuntimeError("Error importing src modules. Check src/preprocess.py and src/save_alert.py: " + str(e))

app = Flask(__name__)
CORS(app)

# MySQL config - change if needed
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",        # set password if your XAMPP MySQL has one
    "database": "fraud_detection"
}

def get_db_conn():
    return mysql.connector.connect(**DB_CONFIG)

# Load model
MODEL_PATH = os.path.join(MODELS, "fraud_model.pkl")
if not os.path.exists(MODEL_PATH):
    # fallback - in case models/ is placed differently
    MODEL_PATH = os.path.join(ROOT, "..", "models", "fraud_model.pkl")
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Model file not found at: " + MODEL_PATH)
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

def predict_from_dict(input_data):
    df = pd.DataFrame([input_data])
    df_pre = preprocess(df, training=False)
    pred = model.predict(df_pre)[0]
    prob = model.predict_proba(df_pre)[0][1]
    return int(pred), float(prob)

@app.route("/predict", methods=["POST"])
def api_predict():
    payload = request.json
    if not payload:
        return jsonify({"success": False, "error": "Empty payload"}), 400

    missing = [f for f in REQUIRED_FIELDS if f not in payload]
    if missing:
        return jsonify({"success": False, "error": f"Missing fields: {missing}"}), 400

    try:
        pred, prob = predict_from_dict(payload)

        # prepare data to save using your existing save_alert function
        data_to_save = payload.copy()
        data_to_save["label"] = "fraud" if pred == 1 else "legit"
        data_to_save["fraud_probability"] = prob

        try:
            saved = save_alert(data_to_save)   # should return True/False
        except Exception as e:
            # Return prediction but include save error for debugging
            return jsonify({
                "success": True,
                "prediction": pred,
                "fraud_probability": prob,
                "saved": False,
                "save_error": str(e)
            })

        return jsonify({
            "success": True,
            "prediction": pred,
            "fraud_probability": prob,
            "saved": bool(saved)
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/transactions", methods=["GET"])
def api_transactions():
    limit = int(request.args.get("limit", 200))
    try:
        conn = get_db_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM transactions ORDER BY timestamp DESC LIMIT %s", (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/fraud_alerts", methods=["GET"])
def api_alerts():
    limit = int(request.args.get("limit", 200))
    try:
        conn = get_db_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM fraud_alerts ORDER BY timestamp DESC LIMIT %s", (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Starting Flask backend on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
