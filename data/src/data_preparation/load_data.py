import pandas as pd
import numpy as np
from datetime import datetime

LABEL_COL = "Label"
TIME_COL = "Timestamp"


def load_csv(file_path, benign_only=True):
    df = pd.read_csv(file_path)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Normalize label text
    if LABEL_COL in df.columns:
        df[LABEL_COL] = df[LABEL_COL].astype(str).str.strip().str.upper()
        if benign_only:
            df = df[df[LABEL_COL] == "BENIGN"]

    # Parse timestamp and sort
    if TIME_COL in df.columns:
        df[TIME_COL] = pd.to_datetime(df[TIME_COL], errors="coerce")
        df = df.dropna(subset=[TIME_COL])
        df = df.sort_values(TIME_COL)

    # Replace infinities
    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Do not drop NaN here; we will drop only on selected features later
    return df.reset_index(drop=True)
