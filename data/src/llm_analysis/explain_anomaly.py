import numpy as np
import subprocess
from pathlib import Path

from feature_deviation import compute_feature_deviation
from prompt_builder import build_prompt
from data.src.data_preparation.config import FEATURES

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT /  "processed"


def run_llm(prompt):
    result = subprocess.run(
        ["ollama", "run", "mistral"],
        input=prompt,
        capture_output=True,
        encoding="utf-8",
        errors="ignore"
    )
    return result.stdout


def main():
    # Load one detected anomaly (example)
    X_attack = np.load(DATA_DIR / "X_attack.npy")
    benign_mean = np.load(DATA_DIR / "X_train.npy").mean(axis=(0, 1))

    anomalous_window = X_attack[0]  # demo

    deviation = compute_feature_deviation(
        anomalous_window,
        benign_mean,
        FEATURES
    )

    prompt = build_prompt(deviation)
    explanation = run_llm(prompt)

    print("🧠 LLM EXPLANATION")
    print(explanation)


if __name__ == "__main__":
    main()