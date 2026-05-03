import numpy as np

def compute_feature_deviation(window, benign_mean, feature_names):
    """
    window: (timesteps, features)
    benign_mean: (features,)
    """

    window_mean = window.mean(axis=0)
    deviation = window_mean - benign_mean

    deviation_dict = {}

    for i, feat in enumerate(feature_names):
        deviation_dict[feat] = deviation[i]

    return deviation_dict