from db_connection import get_connection
import pandas as pd

def load_transactions():
    conn = get_connection()
    query = "SELECT * FROM transactions"
    df = pd.read_sql(query, conn)
    conn.close()
    return df
