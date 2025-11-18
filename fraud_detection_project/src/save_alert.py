# src/save_alert.py
import mysql.connector
from mysql.connector import Error
from datetime import datetime

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "fraud_detection"
}

THRESHOLD = 0.60   # 60%

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def ensure_user_exists(cur, user_id):
    cur.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO users (user_id, name) VALUES (%s, %s)", (user_id, f"User_{user_id}"))

def ensure_device_exists(cur, device_id, user_id=None):
    cur.execute("SELECT 1 FROM devices WHERE device_id = %s", (device_id,))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO devices (device_id, user_id, device_type, os, ip_address) VALUES (%s, %s, %s, %s, %s)",
            (device_id, user_id, "unknown", "unknown", "0.0.0.0")
        )

def save_alert(data):
    """
    Save transaction always. Save entry to fraud_alerts only if fraud_probability >= THRESHOLD.
    data: dict with keys amount, timestamp, transaction_type, location, user_id, device_id, label, fraud_probability, optional transaction_id
    Returns True on success, False on DB error (rolled back).
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        user_id = int(data.get("user_id"))
        device_id = int(data.get("device_id"))
        txn_id = data.get("transaction_id")  # may be None
        fraud_prob = float(data.get("fraud_probability", 0))
        predicted_label = data.get("label", "unknown")
        ts = data.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ensure user/device exist
        ensure_user_exists(cur, user_id)
        ensure_device_exists(cur, device_id, user_id)

        # If transaction_id is None or empty, pass None -> MySQL will auto-increment if column is AUTO_INCREMENT
        if not txn_id:
            txn_id = None

        sql_txn = """
            INSERT INTO transactions
            (transaction_id, user_id, amount, transaction_type, location, device_id, timestamp, label)
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

        # determine inserted transaction id if not provided
        if txn_id is None:
            txn_id = cur.lastrowid

        # create alert only if probability crosses threshold
        if fraud_prob >= THRESHOLD:
            sql_alert = """
                INSERT INTO fraud_alerts (transaction_id, predicted_label, confidence, timestamp)
                VALUES (%s, %s, %s, %s)
            """
            cur.execute(sql_alert, (txn_id, predicted_label, fraud_prob, ts))

        conn.commit()
        cur.close()
        return True

    except Error as e:
        print("[❌] DB Error:", e)
        if conn:
            conn.rollback()
        return False

    finally:
        if conn and conn.is_connected():
            conn.close()
