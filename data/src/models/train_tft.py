import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import matplotlib.pyplot as plt

from tft_model import TFTAutoencoder
from config import *
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "processed"
MODEL_DIR = PROJECT_ROOT / "models_saved"
RESULTS_DIR = PROJECT_ROOT / "results" / "training"

MODEL_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    X_train = np.load(DATA_DIR / "X_train.npy")
    X_val = np.load(DATA_DIR / "X_val.npy")

    X_train = torch.tensor(X_train, dtype=torch.float32)
    X_val = torch.tensor(X_val, dtype=torch.float32)

    return X_train, X_val


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    X_train, X_val = load_data()

    train_loader = DataLoader(
        TensorDataset(X_train),
        batch_size=BATCH_SIZE,
        shuffle=True
    )

    val_loader = DataLoader(
        TensorDataset(X_val),
        batch_size=BATCH_SIZE
    )

    model = TFTAutoencoder(
        input_size=INPUT_SIZE,
        hidden_size=HIDDEN_SIZE,
        num_heads=NUM_HEADS,
        num_layers=NUM_LAYERS,
        dropout=DROPOUT
    ).to(device)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # 🔹 Store losses
    train_losses = []
    val_losses = []

    # ---------------- Training ----------------
    for epoch in range(EPOCHS):
        model.train()
        train_loss = 0

        for (x,) in train_loader:
            x = x.to(device)

            optimizer.zero_grad()
            recon = model(x)
            loss = criterion(recon, x)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        model.eval()
        val_loss = 0
        with torch.no_grad():
            for (x,) in val_loader:
                x = x.to(device)
                recon = model(x)
                val_loss += criterion(recon, x).item()

        avg_train_loss = train_loss / len(train_loader)
        avg_val_loss = val_loss / len(val_loader)

        train_losses.append(avg_train_loss)
        val_losses.append(avg_val_loss)

        print(
            f"Epoch {epoch+1}/{EPOCHS} | "
            f"Train Loss: {avg_train_loss:.6f} | "
            f"Val Loss: {avg_val_loss:.6f}"
        )

    # ---------------- Save Model ----------------
    torch.save(model.state_dict(), MODEL_DIR / "tft_autoencoder.pth")
    print("✅ Model saved successfully")

    # ---------------- Save Training Results ----------------

    # 1️⃣ Save loss curve
    plt.figure()
    plt.plot(train_losses, label="Train Loss")
    plt.plot(val_losses, label="Validation Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Reconstruction Loss")
    plt.title("TFT Training Loss Curve")
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "loss_curve.png")
    plt.close()

    # 2️⃣ Save numeric log
    with open(RESULTS_DIR / "training_log.txt", "w") as f:
        for i, (t, v) in enumerate(zip(train_losses, val_losses)):
            f.write(f"Epoch {i+1}: Train={t:.6f}, Val={v:.6f}\n")

    print("📊 Training plots and logs saved successfully")


if __name__ == "__main__":
    main()
