#### Preamble ####
# Purpose: Generates neighbourhood clusters based on Toronto Census profile data.
# Author: Mike Cowan
# Date: 19 May 2025
# Contact: m.cowan@mail.utoronto.ca
# License: MIT
# Pre-requisites:
# - `polars` must be installed (pip install polars)
# - `numpy` must be installed (pip install numpy)
# - `matplotlib` must be installed (pip install matplotlib)
# - `scikit-learn` must be installed (pip install scikit-learn)
# - Note: attaching labels was working before when functioning off the silhouette, will fix ASAP.

#### Workspace setup ####
import polars as pl
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import (
    StandardScaler,
)  # Brings each variable to mean 0 / std 1 so no one feature dominates
from sklearn.cluster import (
    KMeans,
)  # Separate into k groups by minimizing within‐cluster variance
from sklearn.metrics import (
    silhouette_score,
)
from sklearn.decomposition import PCA

# [https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html]
# [https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html]
# [https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html]
# [https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html]

# Set random seed for reproducibility
np.random.seed(838)

# Load SES features
profiles = pl.read_csv("data/02-analysis_data/merged_data.csv")
feature_cols = [
    "education_rate",  # proportion adults with a bachelor’s degree or higher
    "prop_single_parent",  # proportion of single-parent households
    "unemployment_rate",  # % of the labour force unemployed
    "median_income",  # median household income
]
# Convert the select columns to a float array
X = profiles.select(feature_cols).to_numpy().astype(float)

# Scale features so each has mean=0, std=1 (prevents any one feature dominating)
# [https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# Find the best k via silhouette score (higher is better: range [-1,1])
best_k, best_score = 3, -1
for k in range(2, 7):
    labels = KMeans(n_clusters=k, random_state=42).fit_predict(X_scaled)
    score = silhouette_score(X_scaled, labels)
    print(f"k={k}  silhouette={score:.3f}")
    if score > best_score:
        best_k, best_score = k, score
print(f">>> best k = {best_k} (silhouette={best_score:.3f})\n")

#### K-Means Cluster Model ####
# Fit K-Means (k=3), attach integer cluster labels
# [https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html#sklearn.cluster.KMeans.labels]
kmeans = KMeans(n_clusters=3, random_state=42).fit(X_scaled)
profiles = profiles.with_columns(
    pl.Series("cluster", kmeans.labels_)  # cluster ∈ {0,1,2}
)

# Summary stats for each cluster
cluster_stats = (
    profiles.group_by("cluster")
    .agg(
        [
            pl.count("neighbourhood").alias("n"),
            pl.mean("education_rate").alias("avg_education_rate"),
            pl.mean("prop_single_parent").alias("avg_single_parent_share"),
            pl.mean("unemployment_rate").alias("avg_unemployment_rate"),
            pl.mean("median_income").alias("avg_median_income"),
        ]
    )
    .sort("cluster")
)
print("Cluster summaries:")
print(cluster_stats)

# Show which neighbourhoods fell into each cluster
clustered = profiles.select(["neighbourhood", "cluster"]).sort(
    ["cluster", "neighbourhood"]
)
print("\nNeighbourhood assignments:")
print(clustered)

#### Save cluster data ####
clustered.write_csv("data/02-analysis_data/neighbourhood_clusters.csv")
