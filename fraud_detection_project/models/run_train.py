import sys
import os

# Add paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_PATH = os.path.join(BASE_DIR, "src")
MODELS_PATH = os.path.join(BASE_DIR, "models")

sys.path.append(SRC_PATH)
sys.path.append(MODELS_PATH)

# Imports
from load_data import load_transactions
from preprocess import preprocess
from train_model import train_model

# Pipeline
df = load_transactions()
df_pre = preprocess(df)
train_model(df_pre)

