import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from config import PROCESSED_DATA_DIR, FEATURES


def load_training_data():
    X_train = np.load(PROCESSED_DATA_DIR / "X_train.npy")
    return X_train


def flatten_windows(X):
    """
    (n_windows, timesteps, n_features) -> (n_windows*timesteps, n_features)
    """
    return X.reshape(-1, X.shape[-1])


def variance_analysis(X_flat, feature_names, threshold=1e-5):
    variances = np.var(X_flat, axis=0)
    var_df = pd.DataFrame(
        {"Feature": feature_names, "Variance": variances}
    ).sort_values(by="Variance", ascending=True)

    low_var = var_df[var_df["Variance"] < threshold]

    print("\n🔹 Variance Analysis")
    print(var_df)
    print(f"\n⚠️ Features below variance threshold {threshold}:")
    print(low_var["Feature"].tolist() if not low_var.empty else "None")

    return var_df, low_var["Feature"].tolist()


def correlation_analysis(X_flat, feature_names, threshold=0.95):
    corr = pd.DataFrame(X_flat, columns=feature_names).corr()

    print(f"\n🔹 Highly correlated feature pairs (>|{threshold}|):")
    high_corr_pairs = []
    n = len(feature_names)
    for i in range(n):
        for j in range(i + 1, n):
            c = corr.iloc[i, j]
            if abs(c) > threshold:
                pair = (feature_names[i], feature_names[j], float(c))
                high_corr_pairs.append(pair)
                print(f"{pair[0]} ↔ {pair[1]} : {pair[2]:.3f}")

    # Heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, cmap="coolwarm", square=True, annot=False)
    plt.title("Feature Correlation Heatmap")
    plt.tight_layout()
    plt.show()

    # Simple rule: keep the first feature, mark the others in each pair to drop
    to_drop = set()
    for f1, f2, _ in high_corr_pairs:
        if f2 not in to_drop:
            to_drop.add(f2)

    return corr, sorted(list(to_drop))


def main():
    print("🔹 Loading training data...")
    X_train = load_training_data()

    print("🔹 Flattening windows...")
    X_flat = flatten_windows(X_train)

    # Use FEATURES from config
    feature_names = FEATURES

    var_df, low_var_features = variance_analysis(X_flat, feature_names)

    corr, corr_drop_features = correlation_analysis(
        X_flat, feature_names, threshold=0.95
    )

    # Combine recommendations
    drop_features = sorted(list(set(low_var_features) | set(corr_drop_features)))
    keep_features = [f for f in feature_names if f not in drop_features]

    print("\n🔹 Recommended features to DROP:")
    print(drop_features if drop_features else "None")

    print("\n🔹 Recommended features to KEEP:")
    print(keep_features)

    # Save to disk so preprocessing / model code can reuse
    feature_info = {
        "all_features": feature_names,
        "keep_features": keep_features,
        "drop_features": drop_features,
        "variance_table": var_df,
    }
    joblib.dump(feature_info, PROCESSED_DATA_DIR / "feature_info.pkl")
    print(f"\n✅ Saved feature info to {PROCESSED_DATA_DIR / 'feature_info.pkl'}")


if __name__ == "__main__":
    main()
