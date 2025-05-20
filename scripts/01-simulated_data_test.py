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
    return pl.read_csv("data/00-simulated_data/simulated_data.csv")


# Check that there are 158 rows (neighbourhoods in Toronto; height in polars)
# [https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.height.html]
def test_row_count(df):
    assert df.height == 158, f"Looking for 158 rows, found {df.height}"


# Check how many columns (width in polars)
# [https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.width.html]
def test_column_count(df):
    assert df.width == 15, f"Looking for 17 columns, got {df.width}."


# Check that the neighbourhoods are unique
def test_unique_neighbourhoods(df):
    n_unique = df.select(pl.col("neighbourhood").n_unique()).item()
    assert (
        n_unique == df.height
    ), "Neighbourhood names are not unique, check for duplicates"


# Check for missing values
def test_no_missing(df):
    # sum of null counts across all cols should be zero
    total_nulls = df.null_count().to_series().sum()
    assert total_nulls == 0, f"Found {total_nulls} missing values"


# Check that all columns are the expected type
def test_variable_types(df):
    expected_dict = {
        "neighbourhood": pl.Utf8,
        "single_parent_families": pl.Int64,
        "two_parent_families": pl.Int64,
        "prop_single_parent": pl.Float64,
        "assault": pl.Int64,
        "robbery": pl.Int64,
        "breakenter": pl.Int64,
        "homicide": pl.Int64,
        "shooting": pl.Int64,
        "assault_rate": pl.Float64,
        "robbery_rate": pl.Float64,
        "breakenter_rate": pl.Float64,
        "homicide_rate": pl.Float64,
        "shooting_rate": pl.Float64,
    }
    for col, expected_dict in expected_dict.items():
        actual_dict = df.schema.get(col)
        assert (
            actual_dict == expected_dict
        ), f"{col} has type {actual_dict}, expected {expected_dict}"


# Check that the crime incidents are between 0 and 1
def test_negative_counts(df):
    count_cols = ["assault", "robbery", "breakenter", "homicide", "shooting"]
    for c in count_cols:
        mn = df.select(pl.col(c).min()).item()
        assert mn >= 0, f"Crime count column {c} has negative values (min = {mn})"


# Check that the crime rates are plausible (0-2500 per 100K people)
def test_rates_plausible(df):
    rate_cols = [
        "assault_rate",
        "robbery_rate",
        "breakenter_rate",
        "homicide_rate",
        "shooting_rate",
    ]
    for c in rate_cols:
        # alias the min-max aggregates
        mn, mx = df.select(
            pl.col(c).min().alias(f"{c}_min"),
            pl.col(c).max().alias(f"{c}_max"),
        ).row(0)
        assert 0 <= mn < 10_000, f"{c} min {mn} out of range"
        assert 0 <= mx < 10_000, f"{c} max {mx} out of range"


# Check that the single-parent family share is between real bounds (~0.05, 0.55)
def test_single_parent_prop(df):
    single_parent_min = df.select(pl.col("prop_single_parent").min()).item()
    single_parent_max = df.select(pl.col("prop_single_parent").max()).item()
    assert (
        single_parent_min >= 0.05
    ), f"Single-parent proportion {single_parent_min} below minimum (0.05)"
    assert (
        single_parent_max <= 0.55
    ), f"Single-parent proportion {single_parent_max} above maximum (0.55)"
