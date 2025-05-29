#### Preamble ####
# Purpose: Plots 2019-2024 crime trend data by Toronto neighbourhood clusters.
# Author: Mike Cowan
# Date: 19 May 2025
# Contact: m.cowan@mail.utoronto.ca
# License: MIT
# Pre-requisites:
# - `polars` must be installed (pip install polars)
# - `matplotlib` must be installed (pip install matplotlib)

#### Workspace setup ####
import polars as pl
import matplotlib.pyplot as plt
from pathlib import Path  # inherent to Python


#### MAIN FUNCTION ####
def main():
    print("Plotting crime trends by neighbourhood clusters (2019–2024).")

    #### 07.0-plot_crime_clusters.py ####
    #### Load data ####
    merged_data = pl.read_csv("data/02-analysis_data/02-analysis_data_merged.csv")
    crime_types = ["assault", "breakenter", "robbery", "shooting"]
    years = [2019, 2020, 2021, 2022, 2023, 2024]

    # Specify figures directory
    png_directory = Path("other/figures")
    png_directory.mkdir(parents=True, exist_ok=True)

    # 2x2 subplot figure for combined trends plot
    # [https://matplotlib.org/stable/gallery/subplots_axes_and_figures/subplot_demo.html]
    fig_combined, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes = axes.flatten()

    # Loop through each crime and save plots
    for idx, crime in enumerate(crime_types):
        # Build rate column names for each year
        rate_columns = [f"{crime}_rate_{y}" for y in years]

        # Unpivot wide to long for time-series, extract year as integer (like pivot_longer)
        # Before: Columns = years, Rows = neighborhoods
        # After: Rows = neighborhood-year combinations, Columns = [SES, year, rate]
        # [https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.unpivot.html#polars.DataFrame.unpivot]
        merged_long = (
            merged_data.select(
                ["opportunity_index", *rate_columns]
            )  # * = "and all individual columns from list"
            .unpivot(
                on=rate_columns,
                index="opportunity_index",
                variable_name="year",
                value_name="rate",
            )
            .with_columns(pl.col("year").str.extract(r"_(\d{4})$", 1).cast(pl.Int64))
        )

        # Group by SES and year, calculating mean rates
        trend = (
            merged_long.group_by(["opportunity_index", "year"])
            .agg(pl.col("rate").mean().alias("average_rate"))
            .sort(["opportunity_index", "year"])
        )

        # Plot each SES cluster individually
        fig_indiv, ax_indiv = plt.subplots(figsize=(6, 4))
        for lvl in ["Low Opportunity", "Medium Opportunity", "High Opportunity"]:
            sub = trend.filter(pl.col("opportunity_index") == lvl)
            ax_indiv.plot(
                sub["year"].to_list(),
                sub["average_rate"].to_list(),
                marker="o",
                label=lvl,
            )
        # Enhance plot readability
        ax_indiv.set_title(f"{crime.title()} Rate Trends (2019–2024)")
        ax_indiv.set_xlabel("Year")
        ax_indiv.set_ylabel(f"Average {crime.title()} Rate per 100K Persons")
        ax_indiv.legend(title="Opportunity Level")
        fig_indiv.tight_layout()
        fig_indiv.savefig(png_directory / f"{idx+1}_{crime}.png", dpi=300)
        plt.close(fig_indiv)

        # Add crime type to its position in 2x2 grid
        ax_combined = axes[idx]
        for lvl in ["Low Opportunity", "Medium Opportunity", "High Opportunity"]:
            sub = trend.filter(pl.col("opportunity_index") == lvl)
            ax_combined.plot(
                sub["year"].to_list(),
                sub["average_rate"].to_list(),
                marker="o",
                label=lvl,
            )
        ax_combined.set_title(f"{crime.title()} Rate")
        ax_combined.set_xlabel("Year")
        ax_combined.set_ylabel("Rate per 100K")
        ax_combined.legend(title="SES Cluster", fontsize=8)

    #### Save figures ####
    fig_combined.suptitle(
        "Crime Rate Trends by Opportunity Cluster (2019–2024)", fontsize=16
    )
    fig_combined.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig_combined.savefig(png_directory / "fig_1_crime_trends.png", dpi=300)
    plt.close(fig_combined)


#### ENTRY POINT ####
if __name__ == "__main__":
    main()
    print("Crime trends by neighbourhood clusters (2019–2024) have been plotted.")
