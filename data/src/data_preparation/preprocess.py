import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler

from config import FEATURES
from load_data import TIME_COL


def add_time_features(df):
    if TIME_COL not in df.columns:
        return df

    ts = df[TIME_COL]
    df["hour"] = ts.dt.hour
    df["dayofweek"] = ts.dt.dayofweek
    df["is_weekend"] = (df["dayofweek"] >= 5).astype(int)
    return df


EXTRA_TIME_FEATURES = ["hour", "dayofweek", "is_weekend"]
ALL_FEATURES = FEATURES + EXTRA_TIME_FEATURES


def get_available_features(df):
    return [
        f for f in ALL_FEATURES
        if f in df.columns and df[f].dtype != "O"
    ]


def clip_outliers(X, low_q=0.001, high_q=0.999):
    low = np.quantile(X, low_q, axis=0)
    high = np.quantile(X, high_q, axis=0)
    X_clipped = np.clip(X, low, high)
    return X_clipped, low, high


def fit_scaler(df, features):
    # Drop rows with NaN in used features
    df_feat = df.dropna(subset=features)
    X = df_feat[features].values.astype(np.float32)

    X_clipped, low, high = clip_outliers(X)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_clipped)

    meta = {
        "features": features,
        "low": low,
        "high": high,
    }
    return X_scaled, scaler, meta, df_feat.index


def transform_with_scaler(df, scaler, meta):
    features = meta["features"]
    low, high = meta["low"], meta["high"]

    df_feat = df.dropna(subset=features)
    X = df_feat[features].values.astype(np.float32)
    X_clipped = np.clip(X, low, high)
    X_scaled = scaler.transform(X_clipped)

    return X_scaled, df_feat.index
