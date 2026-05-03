import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "processed"


def main():
    train_errors = np.load(DATA_DIR / "train_errors.npy")

    # Percentile-based threshold (robust)
    percentile = 99.5
    threshold = np.percentile(train_errors, percentile)

    print("🔹 Threshold calculation (Percentile-based)")
    print(f"Percentile used : {percentile}")
    print(f"Anomaly thresh  : {threshold:.6f}")

    np.save(DATA_DIR / "threshold.npy", threshold)
    print("✅ Threshold saved")


if __name__ == "__main__":
    main()
