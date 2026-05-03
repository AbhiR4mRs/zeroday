# explain_window.py
from src.llm_analysis.feature_deviation import compute_feature_deviation
from src.llm_analysis.prompt_builder import build_prompt
import numpy as np


def explain_window(window, benign_mean, features, llm_fn, threshold):
    """
    Complete anomaly detection + explanation pipeline.
    
    Args:
        window: (timesteps, features)
        benign_mean: (features,)
        features: list of feature names
        llm_fn: function that takes prompt → explanation
        threshold: float, trained anomaly threshold
    
    Returns:
        (explanation, is_anomaly, anomaly_score)
    """
    deviation = compute_feature_deviation(window, benign_mean, features)
    
    # Anomaly score = max deviation (proxy for reconstruction error)
    anomaly_score = max(abs(v) for v in deviation.values())
    
    if anomaly_score > threshold:
        prompt = build_prompt(deviation)
        explanation = llm_fn(prompt)
        return explanation, True, anomaly_score
    else:
        return "Normal traffic patterns detected.", False, anomaly_score
