#### Preamble ####
# Purpose: Cleans the raw neighbourhood profile data.
# Author: Michael Cowan
# Date: 13 May 2025
# Contact: m.cowan@mail.utoronto.ca
# License: MIT
# Pre-requisites: [...UPDATE THIS...]
# Any other information needed? [...UPDATE THIS...]

#### Workspace setup ####
import polars as pl
import numpy as np

#### Clean neighbourhood profile data ####
# Neighbourhood profile data
profile_df = pl.read_excel("data/01-raw_data/neighbourhood_profiles.xlsx")

# Stripping whitespace only from specific columns (Neighborhood Name)
# (https://sparkbyexamples.com/polars/strip-entire-polars-dataframe/)
profile_df = profile_df.with_columns(pl.col("Neighbourhood Name").str.strip_chars(" "))

# Filter to only the two rows we want (the first to appear)
profile_df = profile_df.filter(
    pl.col("Neighbourhood Name").is_in(
        ["With children", "One-parent-family households"]
    )
).head(2)

# Need to flip the spreadsheet to merge (transpose: rows become columns and vice versa)
# (https://sparkbyexamples.com/polars/polars-transpose-dataframe/)
profile_transposed = profile_df.transpose(
    include_header=True,  # bring the original column names
    header_name="neighbourhood",  # rename the header column (1st column)
    column_names=[
        "two-parent families",
        "one-parent families",
    ],  # rename the subsequent columns
)

# Slice redundant row (duplicate header)
# https://sparkbyexamples.com/polars/polars-dataframe-slice-usage-examples/
profile_transposed = profile_transposed.slice(1)

#### Save data ####
profile_transposed.write_csv("data/02-analysis_data/analysis_data_profiles.csv")
