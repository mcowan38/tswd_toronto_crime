#### Preamble ####
# Purpose: Tests the merged neighbourhood crime and Census profile data.
# Author: Mike Cowan
# Date: 19 May 2025
# Contact: m.cowan@mail.utoronto.ca
# License: MIT
# Pre-requisites:
# - `polars` must be installed (pip install polars)
# - `pytest` must be installed (pip install pytest); run with "pytest -q"
# References:
# - [https://docs.pytest.org/en/stable/]

#### Workspace setup ####
import polars as pl
import pytest  # test functions across any .py ending with "test"


#### Test data ####
# Test if data loads correctly (uses fixture function to try to read simulate_ data.csv)
@pytest.fixture
def sim_data():
    return pl.read_csv("data/00-simulated_data/simulated_data.csv")


# Check that there are actually 158 rows (neighbourhoods in Toronto; height in polars)
# [https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.height.html]
def test_row_count(sim_data):
    # assert = if the condition is not met, raise an error with the message (from the f-string literal)
    assert sim_data.height == 158, f"Expected 158 rows, found {sim_data.height}"


# Check how many columns (width in polars)
# [https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.width.html]
def test_column_count(sim_data):
    assert sim_data.width == 15, f"Expected 15 columns, found {sim_data.width}"


# Check that the neighbourhoods are unique
# [https://docs.pola.rs/api/python/stable/reference/series/api/polars.Series.n_unique.html]
def test_column_count(sim_data):
    assert sim_data.width == 15, f"Expected 15 columns, found {sim_data.width}"


# Check for missing values
# [https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.null_count.html]
def test_no_missing(sim_data):
    # sum of null counts across all columns should be zero
    total_nulls = sim_data.null_count().to_series().sum()
    assert total_nulls == 0, f"Found {total_nulls} missing values"


# Check that all columns have th correct data type (compared data to the map; e.g., integers for counts, floats for proportion/rates)
# Polars DFs have schemas (.schema) that map column names to data types
# [https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.schema.html]
def test_variable_types(sim_data):
    expected_types = {
        "neighbourhood": pl.Utf8,  # character/string data
        "single_parent_families": pl.Int64,  # integer count
        "two_parent_families": pl.Int64,
        "prop_single_parent": pl.Float64,  # proportion (float between 0 and 1)
        "assault": pl.Int64,
        "robbery": pl.Int64,
        "breakenter": pl.Int64,
        "homicide": pl.Int64,
        "shooting": pl.Int64,
        "assault_rate": pl.Float64,  # crime rates (standardized per 100K people)
        "robbery_rate": pl.Float64,
        "breakenter_rate": pl.Float64,
        "homicide_rate": pl.Float64,
        "shooting_rate": pl.Float64,
    }
    for col, expected_type in expected_types.items():
        actual_type = sim_data.schema.get(col)  # get column type from DataFrame schema
        assert (
            actual_type
            == expected_type  # compare schema to the manually written dictionary (expected_types)
        ), f"{col} has type {actual_type}, expected {expected_type}"


# Check that the crime incidents = 0 or greater
# [https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.min.html]
def test_non_negative_counts(sim_data):
    crime_columns = ["assault", "robbery", "breakenter", "homicide", "shooting"]
    for column in crime_columns:
        min_value = sim_data.select(pl.col(column).min()).item()
        assert (
            min_value >= 0
        ), f"Crime count column {column} has negative values (min =  {min_value})"


# Check that the crime rates are actually plausible (guesstimating 0-2500 per 100K people)
def test_plausible_rates(sim_data):
    rate_columns = [
        "assault_rate",
        "robbery_rate",
        "breakenter_rate",
        "homicide_rate",
        "shooting_rate",
    ]
    for column in rate_columns:
        # Select the min-max aggregates from the column
        min, max = sim_data.select(
            pl.col(column).min().alias(f"{column}_min"),
            pl.col(column).max().alias(f"{column}_max"),
        ).row(0)
        assert 0 <= min < 10_000, f"{column} min {min} out of range"
        assert 0 <= max < 10_000, f"{column} max {max} out of range"


# Check that the single-parent family proportions are between real bounds from a glimpse at the actual data (~0.05, 0.55)
def test_single_parent_prop(sim_data):
    single_parent_min = sim_data.select(pl.col("prop_single_parent").min()).item()
    single_parent_max = sim_data.select(pl.col("prop_single_parent").max()).item()
    assert (
        single_parent_min >= 0.05
    ), f"Single-parent proportion {single_parent_min} is below minimum (0.05)"
    assert (
        single_parent_max <= 0.55
    ), f"Single-parent proportion {single_parent_max} is above maximum (0.55)"
