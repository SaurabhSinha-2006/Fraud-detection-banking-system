import mysql.connector
from mysql.connector import Error
from datetime import datetime

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "fraud_detection"
}

THRESHOLD = 0.60   # 60% fraud probability


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def ensure_user_exists(cur, user_id):
    cur.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO users (user_id, name) VALUES (%s, %s)",
            (user_id, f"User_{user_id}")
        )


def ensure_device_exists(cur, device_id, user_id=None):
    cur.execute("SELECT 1 FROM devices WHERE device_id = %s", (device_id,))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO devices (device_id, user_id, device_type, os, ip_address) "
            "VALUES (%s, %s, %s, %s, %s)",
            (device_id, user_id, "unknown", "unknown", "0.0.0.0")
        )


def save_alert(data):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Convert IDs properly
        user_id = int(data.get("user_id"))
        device_id = int(data.get("device_id"))
        txn_id = data.get("transaction_id")

        fraud_prob = float(data.get("fraud_probability", 0))
        predicted_label = data.get("label", "unknown")
        ts = data.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # --- Ensure user and device exist ---
        ensure_user_exists(cur, user_id)
        ensure_device_exists(cur, device_id, user_id)

        # --- Insert transaction ---
        sql_txn = """
            INSERT INTO transactions
            (transaction_id, user_id, amount, transaction_type,
             location, device_id, timestamp, label)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cur.execute(sql_txn, (
            txn_id,
            user_id,
            float(data["amount"]),
            data["transaction_type"],
            data["location"],
            device_id,
            ts,
            predicted_label
        ))

        print("[✔] Transaction saved successfully.")

        # --- Insert alert ONLY if fraud_prob > threshold ---
        if fraud_prob >= THRESHOLD:
            sql_alert = """
                INSERT INTO fraud_alerts
                (transaction_id, predicted_label, confidence, timestamp)
                VALUES (%s, %s, %s, %s)
            """
            cur.execute(sql_alert, (
                txn_id,
                predicted_label,
                fraud_prob,
                ts
            ))

            print(f"[🚨] Fraud alert generated! (prob={fraud_prob})")

        conn.commit()
        return True

    except Error as e:
        print("[❌] DB Error:", e)
        if conn:
            conn.rollback()
        return False

    finally:
        if conn and conn.is_connected():
            conn.close()
