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

# 1) Read in
crime_df = pl.read_csv("data/02-analysis_data/merged_data.csv")
clusters = pl.read_csv("data/02-analysis_data/neighbourhood_clusters.csv")

# 2) Join in the numeric cluster
crime_df = crime_df.join(
    clusters.select(["neighbourhood", "cluster"]),
    on="neighbourhood",
    how="left",
)

crime_df = crime_df.with_columns(
    pl.when(pl.col("cluster") == 0)
    .then("High Opportunity")
    .when(pl.col("cluster") == 1)
    .then("Medium Opportunity")
    .when(pl.col("cluster") == 2)
    .then("Low Opportunity")
    .otherwise("Unknown")
    .alias("Opportunity_Level")
)


# 4) Fill any missing *_rate_ columns with 0.0
crime_types = ["assault", "breakenter", "robbery", "shooting"]
years = [2019, 2020, 2021, 2022, 2023, 2024]
rate_cols = [f"{c}_rate_{y}" for c in crime_types for y in years]
crime_df = crime_df.with_columns(
    [pl.col(col).fill_null(0.0).alias(col) for col in rate_cols]
)

# 5) Melt (you can continue to use .melt, or switch to .unpivot if you prefer)
for crime in crime_types:
    mv = [f"{crime}_rate_{y}" for y in years]

    df_long = (
        crime_df.select(["Opportunity_Level", *mv])
        .melt(
            id_vars="Opportunity_Level",
            value_vars=mv,
            variable_name="year",
            value_name="rate",
        )
        .with_columns(
            pl.col("year").str.extract(r"_(\d{4})$", 1).cast(pl.Int64).alias("year")
        )
    )

    # 6) Filter only Low & High
    trend = (
        df_long.filter(
            pl.col("Opportunity_Level").is_in(["Low Opportunity", "High Opportunity"])
        )
        .group_by(["Opportunity_Level", "year"])
        .agg(pl.mean("rate").alias("avg_rate"))
        .sort(["Opportunity_Level", "year"])
        .to_pandas()
    )

    # 7) Plot
    plt.figure(figsize=(6, 4))
    for lvl in ["Low Opportunity", "High Opportunity"]:
        sub = trend[trend["Opportunity_Level"] == lvl]
        plt.plot(sub["year"], sub["avg_rate"], marker="o", label=lvl)

    plt.title(f"{crime.title()} Rate Trends (2019–2024)")
    plt.xlabel("Year")
    plt.ylabel(f"Avg {crime.title()} Rate per 100 k")
    plt.legend(title="Opportunity Level")
    plt.tight_layout()
    plt.show()
