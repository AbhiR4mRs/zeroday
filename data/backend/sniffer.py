import time
import json
import redis
import numpy as np
import random
from pathlib import Path
import joblib

from data.src.data_preparation.config import FEATURES, WINDOW_SIZE


# Connect to Redis (producer)
r = redis.Redis(host="localhost", port=6379, db=0)
print("📡 Sniffer module started. Connected to Redis.")

BASE_DIR = Path(__file__).resolve().parents[1]
SCALER_META_PATH = BASE_DIR / "processed" / "scaler_meta.pkl"

scaler_meta = joblib.load(SCALER_META_PATH)
scaler = scaler_meta["scaler"]
low = scaler_meta["meta"]["low"]
high = scaler_meta["meta"]["high"]
feat_order = scaler_meta["meta"]["features"]


def generate_mock_flow_raw() -> np.ndarray:
    """
    Simulates a raw feature vector in CICIDS style (10 numeric features).
    Replace with real flow extraction later.
    """
    base_activity = np.random.normal(0.1, 0.05, len(FEATURES))

    # 10% chance of "attack" spike
    if random.random() > 0.9:
        base_activity[0] += 5.0
        base_activity[5] += 10.0

    return base_activity


def scale_flow(raw_vec: np.ndarray) -> list[float]:
    """
    Clips and scales the raw vector using the same scaler
    that was used for training.
    """
    # Ensure correct feature length
    assert raw_vec.shape[0] == len(FEATURES)

    # Clip and scale
    clipped = np.clip(raw_vec, low, high)
    scaled = scaler.transform(clipped.reshape(1, -1))[0]
    return scaled.astype(float).tolist()


def start_sniffing() -> None:
    try:
        while True:
            raw = generate_mock_flow_raw()
            flow_features = scale_flow(raw)

            r.lpush("network_traffic_queue", json.dumps(flow_features))
            r.ltrim("network_traffic_queue", 0, 1000)

            # ~10 flows per second
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n🛑 Sniffer stopped.")


if __name__ == "__main__":
    start_sniffing()
