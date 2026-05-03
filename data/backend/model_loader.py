import torch
import numpy as np
from pathlib import Path

from data.src.models.tft_model import TFTAutoencoder


BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "models_saved" / "tft_autoencoder.pth"
THRESHOLD_PATH = BASE_DIR / "processed" / "threshold.npy"


class ZeroDayDetector:
    def __init__(self) -> None:
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"⚡ Using device: {self.device}")

        # Load threshold
        self.threshold = float(np.load(THRESHOLD_PATH))

        # Must match training config
        self.input_size = 10      # number of features
        self.window_size = 10     # sequence length

        self.model = TFTAutoencoder(
            input_size=self.input_size,
            hidden_size=64,
            num_heads=4,
            num_layers=2,
            dropout=0.1,
        )

        state_dict = torch.load(MODEL_PATH, map_location=self.device)
        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()

        print("✅ TFT model and threshold loaded.")

    def predict(self, window_array: np.ndarray) -> tuple[float, bool]:
        """
        Input:  window_array shape (window_size, features)
        Output: (reconstruction_error, is_anomaly)
        """
        if window_array.ndim != 2:
            raise ValueError(f"Expected 2D array, got {window_array.shape}")
        if window_array.shape[0] != self.window_size:
            raise ValueError(f"Expected window_size={self.window_size}, got {window_array.shape[0]}")
        if window_array.shape[1] != self.input_size:
            raise ValueError(f"Expected features={self.input_size}, got {window_array.shape[1]}")

        x = torch.tensor(window_array, dtype=torch.float32, device=self.device).unsqueeze(0)

        with torch.no_grad():
            recon = self.model(x)
            error = torch.mean((recon - x) ** 2).item()

        is_anomaly = error > self.threshold
        return error, is_anomaly
