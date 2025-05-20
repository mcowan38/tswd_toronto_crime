#### Preamble ####
# Purpose: Tests the merged neighbourhood crime and Census profile data.
# Author: Mike Cowan
# Date: 19 May 2025
# Contact: m.cowan@mail.utoronto.ca
# License: MIT
# Pre-requisites:
# - `polars` must be installed (pip install polars)
# - `pytest` must be installed (pip install pytest); run with "pytest -q"

#### Workspace setup ####
import polars as pl
import pytest


#### Test data ####
# Test if data loads correctly
@pytest.fixture
def df():
    return pl.read_csv("data/02-analysis_data/merged_data.csv")


# Check that the dataset has 158 rows (there are 158 neighbourhoods in Toronto; height in polars)
# [https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.height.html]
def test_row_count(df):
    assert df.height == 158, f"Looking for 158 rows, found {df.height}"


# Check how many columns (width in polars)
# [https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.width.html]
def test_column_count(df):
    assert df.width == 70, f"Looking for 70 columns, got {df.width}."


# Check that the neighbourhoods are unique
def test_unique_neighbourhoods(df):
    n_unique = df.select(pl.col("neighbourhood").n_unique()).item()
    assert (
        n_unique == df.height
    ), "Neighbourhood names are not unique, check for duplicates"


# Check for missing values (sum of the null counts across all columns should be zero)
# [https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.null_count.html]
def test_no_missing(df):
    total_nulls = df.null_count().to_series().sum()
    assert total_nulls == 0, f"Found {total_nulls} missing values"


# Check that all columns are the expected type
def test_variable_types(df):
    for crime in ["assault", "robbery", "breakenter", "homicide", "shooting"]:
        for year in range(2019, 2025):
            # check each year‐specific count column is Int64
            assert df.schema[f"{crime}_{year}"] == pl.Int64, (
                f"{crime}_{year} has type {df.schema.get(f'{crime}_{year}')}, "
                f"expected Int64"
            )


# Check that the crime incidents are between 0 and 1
def test_negative_counts(df):
    count_cols = [
        f"{crime}_{year}"
        for crime in ["assault", "robbery", "breakenter", "homicide", "shooting"]
        for year in range(2019, 2025)
    ]
    for c in count_cols:
        mn = df.select(pl.col(c).min()).item()
        assert mn >= 0, f"Crime count column {c} has negative values (min = {mn})"


# Check that the crime rates are plausible (0-2500 per 100K people)
def test_rates_plausible(df):
    rate_cols = [
        f"{crime}_rate_{year}"
        for crime in ["assault", "robbery", "breakenter", "homicide", "shooting"]
        for year in range(2019, 2025)
    ]
    for c in rate_cols:
        mn, mx = df.select(
            pl.col(c).min().alias("mn"),
            pl.col(c).max().alias("mx"),
        ).row(0)
        assert 0 <= mn < 10_000, f"Rate column '{c}' has min {mn} out of range"
        assert 0 <= mx < 10_000, f"Rate column '{c}' has max {mx} out of range"


# Check that the single-parent family proportion is between real bounds (~0.05, 0.55)
def test_single_parent_share(df):
    single_parent_min = df.select(pl.col("prop_single_parent").min()).item()
    single_parent_max = df.select(pl.col("prop_single_parent").max()).item()
    assert (
        single_parent_min >= 0.05
    ), f"Single-parent proportion {single_parent_min} below minimum (0.05)"
    assert (
        single_parent_max <= 0.55
    ), f"Single-parent proportion {single_parent_max} above maximum (0.55)"
