#### Preamble ####
# Purpose: Evaluates model fit of K-means vs. Gaussian clusters (K = 2, K = 3).
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
# - [https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_assumptions.html]

#### Workspace setup ####
import polars as pl
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
)


#### MAIN FUNCTION ####
def main():
    print("Evaluating K-means vs. Gaussian Mixture clustering models ($K$ = 2, 3).")

    #### 08.0-model_evaluation.py ####
    # Load and scale SES features (equal weighting requirement for clustering)
    data = pl.read_csv("data/02-analysis_data/02-analysis_data_merged.csv")
    ses_columns = [
        "education_rate",
        "prop_single_parent",
        "unemployment_rate",
        "median_income",
    ]
    feature_matrix = data.select(ses_columns).to_numpy()
    scaled_matrix = StandardScaler().fit_transform(feature_matrix)

    # PCA for 2D visualization (preserves variance)
    # [https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html]
    pca_coordinates = PCA(n_components=2).fit_transform(scaled_matrix)

    # Define clustering configurations (K-means vs. GMM; K =2, 3) and colour maps
    cluster_configs = [
        ("$K$-means", 2, "Paired", "$K$-means ($K$ = 2)"),
        ("GMM", 2, "Accent", "GMM ($K$ = 2)"),
        ("$K$-means", 3, "Set1", "$K$-means ($K$ = 3)"),
        ("GMM", 3, "Set2", "GMM ($K$ = 3)"),
    ]

    # Plot PCA visualizations in a 2x2 grid
    fig_pca, axes_pca = plt.subplots(2, 2, figsize=(12, 10))
    axes_pca = axes_pca.flatten()

    for idx, (model_type, num_clusters, colormap, title) in enumerate(cluster_configs):
        #### Train models (LLM assistance) ####
        # K-means: Hard assignments; GMM: Probabilistic assignments
        if model_type == "KMeans":
            model = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        else:
            model = GaussianMixture(n_components=num_clusters, random_state=42)

        cluster_labels = model.fit_predict(scaled_matrix)  # cluster assignments
        # Plot PCA results with cluster labels
        # [https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.scatter.html]
        scatter = axes_pca[idx].scatter(
            pca_coordinates[:, 0],
            pca_coordinates[:, 1],
            c=cluster_labels,
            cmap=colormap,
            alpha=0.8,
        )
        axes_pca[idx].set_title(title)
        axes_pca[idx].set_xlabel("Principal Component 1")
        axes_pca[idx].set_ylabel("Principal Component 2")
        axes_pca[idx].legend(*scatter.legend_elements(), title="Cluster")

    fig_pca.suptitle(
        "Dimensionality Reduced Clustering Results ($K$-Means vs. GMM)", fontsize=16
    )
    fig_pca.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig_pca.savefig("other/figures/fig_2_cluster_comparisons.png", dpi=300)

    #### Check PCA scores ####
    # Fit PCA on the scaled matrix (using all components)
    pca_full = PCA().fit(scaled_matrix)

    # Explained variance ratio per component
    print("Explained variance ratio:", pca_full.explained_variance_ratio_)

    # Cumulative explained variance
    print("Cumulative explained variance:", pca_full.explained_variance_ratio_.cumsum())

    # Singular values (proportional to component strengths)
    print("Singular values:", pca_full.singular_values_)

    # Eigenvalues (variance captured by each principal axis)
    eigenvalues = pca_full.explained_variance_
    print("Eigenvalues:", eigenvalues)

    #### Cluster Metrics Evaluation ####
    # Compare models using Silhouette, Davies-Bouldin, and Calinski-Harabasz scores
    # [https://scikit-learn.org/stable/modules/clustering.html#clustering-evaluation]
    evaluation_results = []
    for model_type in ["KMeans", "GMM"]:
        for num_clusters in [2, 3]:
            if model_type == "KMeans":
                model = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
            else:
                model = GaussianMixture(n_components=num_clusters, random_state=42)
            labels = model.fit_predict(scaled_matrix)

            # Silhouette: Cluster separation/cohesion (-1 to 1, higher = better)
            # Davies-Bouldin: Cluster overlap (lower = better)
            # Calinski-Harabasz: Variance ratio (higher = tighter clusters)
            evaluation_results.append(
                {
                    "Model": model_type,
                    "k": num_clusters,
                    "Silhouette": silhouette_score(scaled_matrix, labels),
                    "Davies-Bouldin": davies_bouldin_score(scaled_matrix, labels),
                    "Calinski-Harabasz": calinski_harabasz_score(scaled_matrix, labels),
                }
            )

    # Plot evaluation metrics in a 1x3 grid
    metric_names = ["Silhouette", "Davies-Bouldin", "Calinski-Harabasz"]
    metric_titles = [
        "Silhouette Score (↑ better separation)",
        "Davies–Bouldin Index (↓ less overlap)",
        "Calinski–Harabasz Score (↑ tighter clusters)",
    ]

    fig_metrics, axes_metrics = plt.subplots(1, 3, figsize=(18, 5))
    for i, metric in enumerate(metric_names):
        ax = axes_metrics[i]
        bar_width = 0.35
        x_positions = np.arange(2)  # for K = 2 and K = 3

        #  # Plot KMeans and GMM bars side-by-side
        for j, model_type in enumerate(["KMeans", "GMM"]):
            metric_scores = [
                res[metric] for res in evaluation_results if res["Model"] == model_type
            ]
            offset = x_positions + (j - 0.5) * bar_width
            ax.bar(offset, metric_scores, width=bar_width, label=model_type)

        ax.set_xticks(x_positions)
        ax.set_xticklabels(["$K$ = 2", "$K$ = 3"])
        ax.set_xlabel("Number of Clusters ($K$)")
        ax.set_ylabel(metric)
        ax.set_title(metric_titles[i])
        ax.legend()

    #### Save metrics figure ####
    fig_metrics.suptitle(
        "Clustering Evaluation Metrics ($K$-Means vs. GMM; $K$ = 2, 3)", fontsize=16
    )
    fig_metrics.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig_metrics.savefig("other/figures/fig_3_cluster_metrics.png", dpi=300)

    #### Results Summary Table ####
    # Convert evaluation results to a Polars DataFrame for nice formatting
    eval_df = pl.DataFrame(evaluation_results)

    # Format decimal places (.round)
    eval_table = (
        eval_df.with_columns(
            [
                pl.col("Silhouette").round(3),
                pl.col("Davies-Bouldin").round(3),
                pl.col("Calinski-Harabasz").round(1),
            ]
        )
        .sort(["Model", "k"])  # ordered by type then cluster count
        .rename(
            {
                "Model": "Clustering Algorithm",
                "k": "Clusters ($k$)",
                "Silhouette": "Silhouette Score",
                "Davies-Bouldin": "Davies-Bouldin",
                "Calinski-Harabasz": "Calinski-Harabasz",
            }
        )
    )

    # Preview
    print(eval_table)

    #### Save CSV ####
    eval_table.write_csv("data/02-analysis_data/05-cluster_evaluation_metrics.csv")


#### ENTRY POINT ####
if __name__ == "__main__":
    main()
    print(
        "Model evaluation saved to data/02-analysis_data/05-cluster_evaluation_metrics.csv."
    )
