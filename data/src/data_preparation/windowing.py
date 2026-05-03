import numpy as np
from config import WINDOW_SIZE


def create_windows(data, window_size=WINDOW_SIZE):
    n = len(data) - window_size + 1
    if n <= 0:
        return np.empty((0, window_size, data.shape[1]), dtype=data.dtype)

    windows = []
    for i in range(n):
        windows.append(data[i:i + window_size])
    return np.asarray(windows)
