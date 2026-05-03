import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "processed"


def main():
    # =========================
    # Load data
    # =========================
    train_errors = np.load(DATA_DIR / "train_errors.npy")
    attack_errors = np.load(DATA_DIR / "attack_errors.npy")
    threshold = np.load(DATA_DIR / "threshold.npy")

    # =========================
    # 1. Histogram (Main Plot)
    # =========================
    plt.figure(figsize=(10, 5))

    plt.hist(train_errors, bins=100, alpha=0.6, label="Benign", density=True)
    plt.hist(attack_errors, bins=100, alpha=0.6, label="Attack", density=True)

    plt.axvline(threshold, linestyle="--", label="Threshold")

    plt.xlabel("Reconstruction Error")
    plt.ylabel("Density")
    plt.title("Zero-Day Anomaly Detection using TFT")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # =========================
    # 2. Detection Metrics
    # =========================
    attack_detected = np.mean(attack_errors > threshold)
    false_positive = np.mean(train_errors > threshold)

    print("\n🔹 Detection Results")
    print(f"Attack detection rate : {attack_detected*100:.2f}%")
    print(f"False positive rate   : {false_positive*100:.2f}%")

    # =========================
    # 3. Bar Chart (IMPORTANT)
    # =========================
    metrics = [attack_detected * 100, false_positive * 100]
    labels = ["Detection Rate", "False Positive Rate"]

    plt.figure(figsize=(6, 5))
    plt.bar(labels, metrics)

    plt.ylabel("Percentage (%)")
    plt.title("Detection Performance")
    plt.ylim(0, 100)

    # Value labels
    for i, v in enumerate(metrics):
        plt.text(i, v + 1, f"{v:.2f}%", ha='center')

    plt.tight_layout()
    plt.show()

    # =========================
    # 4. Confusion Matrix
    # =========================
    y_true = np.concatenate([
        np.zeros(len(train_errors)),  # benign = 0
        np.ones(len(attack_errors))   # attack = 1
    ])

    y_pred = np.concatenate([
        train_errors > threshold,
        attack_errors > threshold
    ]).astype(int)

    cm = confusion_matrix(y_true, y_pred)

    disp = ConfusionMatrixDisplay(cm)
    disp.plot()

    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.show()

    # =========================
    # 5. Error Over Time (BONUS)
    # =========================
    all_errors = np.concatenate([train_errors, attack_errors])

    plt.figure(figsize=(10, 4))
    plt.plot(all_errors, label="Reconstruction Error")

    plt.axhline(threshold, linestyle='--', label="Threshold")

    plt.xlabel("Time Step")
    plt.ylabel("Error")
    plt.title("Reconstruction Error Over Time")
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()