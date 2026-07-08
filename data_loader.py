import os
import pandas as pd


def load_data(path: str):
    """Utility to load a CSV file into a pandas DataFrame.
    Returns None if the path doesn't exist or an exception occurs.
    """
    if not os.path.exists(path):
        print(f"load_data: file not found at {path}")
        return None
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        print(f"load_data: failed to read CSV: {e}")
        return None
