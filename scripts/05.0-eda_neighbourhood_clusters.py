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
# References:
# - [https://scikit-learn.org/stable/modules/clustering.html#clustering-evaluation]

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
)  # Measure optimal k via silhouette score (higher is better)


#### MAIN FUNCTION ####
def main():
    print("Generating neighbourhood K-means clusters based on Census profile data.")

    #### 05.0-eda_neighbourhood_clusters.py####
    #### Set random seed for reproducibility ####
    np.random.seed(838)

    #### Load SES features ####
    profiles = pl.read_csv("data/02-analysis_data/02-analysis_data_merged.csv")
    ses_columns = [
        "education_rate",  # proportion adults with a bachelor’s degree or higher
        "prop_single_parent",  # proportion of single-parent households
        "unemployment_rate",  # proportioon of the labour force unemployed
        "median_income",  # median household income
    ]

    # Fill any missing rate columns with 0.0 (float)
    crime_types = ["assault", "breakenter", "robbery", "shooting"]
    years = [2019, 2020, 2021, 2022, 2023, 2024]

    # Create a list of feature columns for the SES and crime rates
    crime_rate_columns = [
        f"{crime}_rate_{year}" for crime in crime_types for year in years
    ]

    # Combine the feature columns with the rate columns
    profiles = profiles.with_columns(
        [pl.col(col).fill_null(0.0).alias(col) for col in crime_rate_columns]
    )

    # Convert the selected SES columns to a float array
    X = profiles.select(ses_columns).to_numpy().astype(float)

    # Scale features so each has mean=0, std=1 (prevents any one feature dominating)
    # [https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Find the best K via silhouette score (higher is better: range [-1,1])
    # [https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html]
    best_k, best_score = 3, -1
    for k in range(2, 7):
        labels = KMeans(n_clusters=k, random_state=42).fit_predict(X_scaled)
        score = silhouette_score(X_scaled, labels)
        print(f"K = {k} silhouette={score:.3f}")
        if score > best_score:
            best_k, best_score = k, score
    print(f"Best K = {best_k} (silhouette={best_score:.3f})\n")

    #### K-means Cluster Model ####
    # Fit K-Means (K = 3), attach integer cluster labels
    # [https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html#sklearn.cluster.KMeans.labels]
    kmeans = KMeans(n_clusters=3, random_state=42).fit(X_scaled)
    profiles = profiles.with_columns(
        pl.Series("cluster", kmeans.labels_)  # cluster ∈ {0,1,2}
    )

    # Map clusters to SES labels
    # [https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html#sklearn.cluster.KMeans.labels_]
    label_map = {0: "High Opportunity", 1: "Medium Opportunity", 2: "Low Opportunity"}

    profiles = profiles.with_columns(
        pl.Series("cluster", kmeans.labels_),
        pl.Series(
            "opportunity_index",  # renamed qualitative category
            [label_map[c] for c in kmeans.labels_],
        ),
    )

    # Summary stats for each cluster
    cluster_stats = (
        profiles.group_by("cluster")
        .agg(
            [
                pl.count("neighbourhood").alias("n"),
                pl.mean("education_rate").alias("average_education_rate"),
                pl.mean("prop_single_parent").alias("average_single_parent_share"),
                pl.mean("unemployment_rate").alias("average_unemployment_rate"),
                pl.mean("median_income").alias("average_median_income"),
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
    profiles.select(["neighbourhood", "cluster", "opportunity_index"]).write_csv(
        "data/02-analysis_data/03-cluster_neighbourhoods.csv"
    )

    # Append cluster info back to merged_data
    profiles.write_csv("data/02-analysis_data/02-analysis_data_merged.csv")


#### ENTRY POINT ####
if __name__ == "__main__":
    main()
    print(
        "Neighbourhood clusters generated and appended to data/02-analysis_data/02-analysis_data_merged.csv."
    )
