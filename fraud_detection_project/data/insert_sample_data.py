import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from db_connection import get_connection
import random, datetime

conn = get_connection()
cursor = conn.cursor()

for i in range(100):
    user_id = random.randint(1,5)
    amount = round(random.uniform(100, 50000), 2)
    t_type = random.choice(["upi", "card", "withdrawal", "deposit"])
    location = random.choice(["Delhi", "Mumbai", "Kolkata", "Chennai"])
    device_id = random.randint(1,5)
    timestamp = datetime.datetime.now() - datetime.timedelta(minutes=random.randint(0,30000))

    cursor.execute("""
        INSERT INTO transactions (user_id, amount, transaction_type, location, device_id, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, amount, t_type, location, device_id, timestamp))

conn.commit()
cursor.close()
conn.close()
