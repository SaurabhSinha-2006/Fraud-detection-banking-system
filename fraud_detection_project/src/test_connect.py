from db_connection import get_connection

conn = get_connection()
print("Connected:", conn.is_connected())
