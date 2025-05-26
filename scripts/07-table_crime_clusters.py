#### Preamble ####
# Purpose: Tables 2019–2024 crime trend data by Toronto neighbourhood clusters.
# Author: Mike Cowan
# Date: 19 May 2025
# Contact: m.cowan@mail.utoronto.ca
# License: MIT
# Pre-requisites:
# - `polars` must be installed (pip install polars)

#### Workspace setup ####
import polars as pl
import itertools  # inherent to Python

#### Load data ####
merged_data = pl.read_csv("data/02-analysis_data/merged_data.csv")

# Set parameters
group_col = "Socioeconomic_index"  # use consistent lowercase naming
crime_types = ["assault", "robbery", "breakenter", "shooting"]
years = range(2019, 2025)

# Collect individual summaries
records = []
for crime, year in itertools.product(crime_types, years):
    colname = f"{crime}_rate_{year}"
    if colname not in merged_data.columns:
        continue

    summary = (
        merged_data.select([group_col, colname])
        .group_by(group_col)
        .agg(pl.mean(colname).alias("avg_rate"))
        .with_columns([pl.lit(crime).alias("crime"), pl.lit(year).alias("year")])
    )
    records.append(summary)

# Combine all
result_df = pl.concat(records)

# Pivot to wide format
wide_df = result_df.pivot(
    values="avg_rate", index=["year", "crime"], columns=group_col
).sort(["year", "crime"])

# Preview output
print(wide_df.head())
