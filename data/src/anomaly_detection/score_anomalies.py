import torch
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from data.src.models.tft_model import TFTAutoencoder
from data.src.models.config import *

from torch.utils.data import DataLoader, TensorDataset


DATA_DIR = Path(__file__).resolve().parents[2] / "processed"
MODEL_PATH = Path(__file__).resolve().parents[2] / "models_saved" / "tft_autoencoder.pth"


# =========================
# Load model
# =========================
def load_model(device):
    model = TFTAutoencoder(
        input_size=INPUT_SIZE,
        hidden_size=HIDDEN_SIZE,
        num_heads=NUM_HEADS,
        num_layers=NUM_LAYERS,
        dropout=DROPOUT
    ).to(device)

    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model.eval()
    return model


# =========================
# Reconstruction error
# =========================
def reconstruction_error(model, X, device, batch_size=256):
    dataset = TensorDataset(torch.tensor(X, dtype=torch.float32))
    loader = DataLoader(dataset, batch_size=batch_size)

    errors = []

    with torch.no_grad():
        for (x,) in loader:
            x = x.to(device)
            recon = model(x)
            batch_error = torch.mean((recon - x) ** 2, dim=(1, 2))
            errors.append(batch_error.cpu().numpy())

    return np.concatenate(errors)


# =========================
# Main
# =========================
def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("🔹 Loading data...")
    X_train = np.load(DATA_DIR / "X_train.npy")
    X_attack = np.load(DATA_DIR / "X_attack.npy")

    model = load_model(device)

    print("🔹 Computing reconstruction errors...")
    train_errors = reconstruction_error(model, X_train, device)
    attack_errors = reconstruction_error(model, X_attack, device)

    np.save(DATA_DIR / "train_errors.npy", train_errors)
    np.save(DATA_DIR / "attack_errors.npy", attack_errors)

    print("✅ Anomaly scores saved")
    print(f"Train error mean: {train_errors.mean():.6f}")
    print(f"Attack error mean: {attack_errors.mean():.6f}")

    # =========================
    # 🔥 1. Histogram (VERY IMPORTANT)
    # =========================
    plt.figure(figsize=(10, 5))

    plt.hist(train_errors, bins=100, alpha=0.6, label="Benign", density=True)
    plt.hist(attack_errors, bins=100, alpha=0.6, label="Attack", density=True)

    plt.xlabel("Reconstruction Error")
    plt.ylabel("Density")
    plt.title("Error Distribution (Train vs Attack)")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # =========================
    # 🔥 2. Box Plot (CLEAN VISUAL)
    # =========================
    plt.figure(figsize=(6, 5))

    plt.boxplot([train_errors, attack_errors], labels=["Benign", "Attack"])

    plt.ylabel("Reconstruction Error")
    plt.title("Error Comparison (Box Plot)")
    plt.tight_layout()
    plt.show()

    # =========================
    # 🔥 3. Mean Comparison (BAR)
    # =========================
    means = [train_errors.mean(), attack_errors.mean()]
    labels = ["Benign", "Attack"]

    plt.figure(figsize=(6, 5))
    plt.bar(labels, means)

    plt.ylabel("Mean Reconstruction Error")
    plt.title("Mean Error Comparison")

    for i, v in enumerate(means):
        plt.text(i, v, f"{v:.4f}", ha='center', va='bottom')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()