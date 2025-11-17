import mysql.connector
from mysql.connector import Error
from datetime import datetime

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",         # change if needed
    "database": "fraud_detection"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def ensure_user_exists(cur, user_id):
    cur.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
    if cur.fetchone() is None:
        # create a minimal placeholder user
        cur.execute("INSERT INTO users (user_id, name) VALUES (%s, %s)", (user_id, f"User_{user_id}"))

def ensure_device_exists(cur, device_id, user_id=None):
    cur.execute("SELECT 1 FROM devices WHERE device_id = %s", (device_id,))
    if cur.fetchone() is None:
        # create a minimal placeholder device; associate with user_id if available
        cur.execute(
            "INSERT INTO devices (device_id, user_id, device_type, os, ip_address) VALUES (%s, %s, %s, %s, %s)",
            (device_id, user_id, "unknown", "unknown", "0.0.0.0")
        )

def save_alert(data):
    """
    data should be a dict containing at least:
      - transaction_id (optional)
      - user_id
      - device_id
      - amount
      - transaction_type
      - location
      - timestamp (string)
      - label  (e.g. 'fraud' or 'legit')
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # normalize ids to ints where appropriate
        user_id = int(data.get("user_id"))
        # device_id might be numeric in your DB; try convert, otherwise keep as string
        try:
            device_id = int(data.get("device_id"))
        except Exception:
            device_id = data.get("device_id")

        # 1) ensure user exists
        ensure_user_exists(cur, user_id)

        # 2) ensure device exists and link to user
        ensure_device_exists(cur, device_id, user_id)

        # 3) insert transaction
        sql = """
            INSERT INTO transactions
            (transaction_id, user_id, amount, transaction_type, location, device_id, timestamp, label)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        txn_id = data.get("transaction_id")  # could be None; if column is AUTO_INCREMENT, pass None
        if txn_id is None:
            txn_id = None

        ts = data.get("timestamp")
        # If timestamp missing, use now in proper format
        if not ts:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        values = (
            txn_id,
            user_id,
            float(data.get("amount", 0)),
            data.get("transaction_type"),
            data.get("location"),
            device_id,
            ts,
            data.get("label", "unknown")
        )

        cur.execute(sql, values)
        conn.commit()
        print("[✔] Transaction saved successfully!")

        cur.close()
        return True

    except Error as e:
        # Provide error message for debugging
        print("[❌] Error saving transaction:", e)
        if conn:
            conn.rollback()
        return False

    finally:
        if conn and conn.is_connected():
            conn.close()
