import numpy as np
from pathlib import Path

from data.src.llm_analysis.feature_deviation import compute_feature_deviation
from data.src.llm_analysis.prompt_builder import build_prompt
from data.src.data_preparation.config import FEATURES
from data.src.llm_analysis.llm_engine import run_llm


BASE_DIR = Path(__file__).resolve().parents[2]
X_TRAIN_PATH = BASE_DIR / "data" / "processed" / "X_train.npy"

# Precompute benign mean once at import (on scaled training data)
benign_mean = np.load(X_TRAIN_PATH).mean(axis=(0, 1))


def explain_window(window_array: np.ndarray) -> str:
    """
    Given a window of traffic (shape: [window_size, features]),
    compute feature deviation and ask the LLM for an explanation.
    """
    deviation = compute_feature_deviation(
        window_array=window_array,
        benign_mean=benign_mean,
        feature_names=FEATURES,
    )

    prompt = build_prompt(deviation)
    explanation = run_llm(prompt)
    return explanation
