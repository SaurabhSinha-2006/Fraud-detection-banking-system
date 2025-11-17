import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from load_data import load_transactions
from preprocess import preprocess

df = load_transactions()
df_pre = preprocess(df)
print(df_pre.head())
