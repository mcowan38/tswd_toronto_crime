#### Preamble ####
# Purpose: Tables 2019–2024 crimee trend data by Toronto neighbourhood clusters (percent change).
# Author: Mike Cowan
# Date: 19 May 2025
# Contact: m.cowan@mail.utoronto.ca
# License: MIT
# Pre-requisites:
# - `polars` must be installed (`pip install polars`)

#### Workspace setup ####
import polars as pl
import itertools  # for generating crime × year combinations

#### Load data ####
merged_data = pl.read_csv(
    "data/02-analysis_data/02-analysis_data_merged.csv"
)  # contains cluster labels and crime-rate columns

# Set parameters
group_columns = "Socioeconomic_index"  # column name for SES cluster grouping
crime_types = ["assault", "robbery", "breakenter", "shooting"]
years = list(range(2019, 2025))  # inclusive range of years

# Collect yearly summaries for each crime type and cluster ####
records = []
for crime, year in itertools.product(crime_types, years):
    col_name = f"{crime}_rate_{year}"
    if col_name not in merged_data.columns:
        continue  # skip if rate column is missing

    # Compute mean rate per 100K residents for each SES cluster
    summary = (
        merged_data.select([group_columns, col_name])
        .group_by(group_columns)
        .agg(pl.mean(col_name).alias("avg_rate"))  # average rate for the specified year
        .with_columns([pl.lit(crime).alias("crime"), pl.lit(year).alias("year")])
    )
    records.append(summary)


# Concatenate all summaries into one DataFrame
def build_result():
    return pl.concat(records) if records else pl.DataFrame()


result_df = build_result()

# Pivot_wider: one row per (crime, year) × columns for each SES cluster
wide_df = result_df.pivot(
    values="avg_rate", index=["crime", "year"], columns=group_columns
).sort(["crime", "year"])

# Identify the SES cluster columns for later calculations
cluster_columns = [c for c in wide_df.columns if c not in ["crime", "year"]]

#### Compute year-to-year percent change for each consecutive year ####
pct_change_exprs = []
for col in cluster_columns:
    # For each target year (excluding the first), compute percent change from the previous year
    for prev_year, curr_year in zip(years[:-1], years[1:]):
        pct_name = f"{col}_pct_{prev_year}_{curr_year}"  # e.g., assault_pct_2019_2020
        expr = (
            pl.when(pl.col("year") == curr_year)
            .then(
                (
                    (pl.col(col) - pl.col(col).shift(1).over("crime"))
                    / pl.col(col).shift(1).over("crime")
                    * 100
                ).round(1)
            )
            .alias(pct_name)
        )
        pct_change_exprs.append(expr)

# Add all percent-change columns to the wide DataFrame
wide_df = wide_df.with_columns(pct_change_exprs)

# Preview
print("\nCrime Trends (2019–2024) with Year-to-Year Percent Changes by SES Cluster:\n")
print(wide_df)

#### Save to CSV ####
wide_df.write_csv("data/02-analysis_data/04-cluster_crime_rates.csv")
