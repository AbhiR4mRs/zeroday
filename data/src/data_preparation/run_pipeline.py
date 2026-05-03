import numpy as np
import joblib
import pandas as pd

from config import (
    RAW_DATA_DIR, PROCESSED_DATA_DIR,
    BENIGN_FILES, ATTACK_FILES, WINDOW_SIZE
)
from load_data import load_csv
from preprocess import (
    add_time_features, get_available_features,
    fit_scaler, transform_with_scaler
)
from windowing import create_windows


def load_and_concat(files, benign_only):
    dfs = []
    for fname in files:
        df = load_csv(RAW_DATA_DIR / fname, benign_only=benign_only)
        df = add_time_features(df)
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


def main():
    print("Loading benign traffic...")
    benign_df = load_and_concat(BENIGN_FILES, benign_only=True)

    features = get_available_features(benign_df)
    print(f"Using features: {features}")

    print("Fitting scaler on benign traffic...")
    X_benign_scaled, scaler, meta, kept_idx = fit_scaler(benign_df, features)

    print("Creating benign windows...")
    X_benign_windows = create_windows(X_benign_scaled, WINDOW_SIZE)

    split = int(0.8 * len(X_benign_windows))
    X_train = X_benign_windows[:split]
    X_val = X_benign_windows[split:]

    np.save(PROCESSED_DATA_DIR / "X_train.npy", X_train)
    np.save(PROCESSED_DATA_DIR / "X_val.npy", X_val)

    joblib.dump(
        {"scaler": scaler, "meta": meta},
        PROCESSED_DATA_DIR / "scaler_meta.pkl"
    )

    print("Loading attack traffic...")
    attack_df = load_and_concat(ATTACK_FILES, benign_only=False)

    scaler_meta = joblib.load(PROCESSED_DATA_DIR / "scaler_meta.pkl")
    scaler = scaler_meta["scaler"]
    meta = scaler_meta["meta"]

    X_attack_scaled, _ = transform_with_scaler(attack_df, scaler, meta)
    X_attack_windows = create_windows(X_attack_scaled, WINDOW_SIZE)

    np.save(PROCESSED_DATA_DIR / "X_attack.npy", X_attack_windows)

    print("✅ Pipeline done.")
    print("Train:", X_train.shape,
          "Val:", X_val.shape,
          "Attack:", X_attack_windows.shape)


if __name__ == "__main__":
    main()
