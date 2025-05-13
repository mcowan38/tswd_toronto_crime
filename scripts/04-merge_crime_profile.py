#### Preamble ####
# Purpose: Merges the cleaned neighbourhood crime and profile data.
# Author: Michael Cowan
# Date: 13 May 2025
# Contact: m.cowan@mail.utoronto.ca
# License: MIT
# Pre-requisites: [...UPDATE THIS...]
# Any other information needed? [...UPDATE THIS...]

#### Workspace setup ####
import polars as pl

#### Merge neighbourhood crime and profile data ####
# Load cleaned neighbourhood crime df
crime_df = pl.read_csv("data/02-analysis_data/analysis_data_crime.csv")

# Load cleaned neighbourhood profile df
profile_df = pl.read_csv("data/02-analysis_data/analysis_data_profiles.csv")

# Merge the two dataframes on the neighbourhood column
# (https://dataguymichael.substack.com/p/the-ultimate-polars-cheat-sheet-for)
merged_df = crime_df.join(
    profile_df,
    on="neighbourhood",
    how="left",  # keep rows from right dataframe (profile_df).
)

# Reorder columns via select (recommended method); one-parent-family households first, then two-parent families, etc.
# (https://stackoverflow.com/questions/71353113/polars-how-to-reorder-columns-in-a-specific-order)
merged_df = merged_df.select(
    [
        pl.col("neighbourhood"),
        pl.col("one-parent families"),
        pl.col("two-parent families"),
        pl.col("assault_count"),
        pl.col("assault_rate"),
        pl.col("break-enter_count"),
        pl.col("break-enter_rate"),
        pl.col("homicide_count"),
        pl.col("homicide_rate"),
        pl.col("robbery_count"),
        pl.col("robbery_rate"),
        pl.col("shooting_count"),
        pl.col("shooting_rate"),
    ]
)

#### Save data ####
merged_df.write_csv("data/02-analysis_data/merged_data.csv")
