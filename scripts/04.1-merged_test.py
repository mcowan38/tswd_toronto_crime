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
# - [https://docs.pytest.org/en/stable]

#### Workspace setup ####
import polars as pl
import pytest  # test functions across any .py ending with "test"


#### Test data ####
# Test if data loads correctly (uses fixture function to try to read 02-analysis_data_merged.csv)
@pytest.fixture
def merged_data():
    return pl.read_csv("data/02-analysis_data/02-analysis_data_merged.csv")


# Check that the dataset has 158 rows (there are 158 neighbourhoods in Toronto; height in polars)
# [https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.height.html]
def test_row_count(merged_data):
    assert (
        merged_data.height == 158
    ), f"Looking for 158 rows, found {merged_data.height}"


# Check how many columns (width in polars)
# [https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.width.html]
def test_column_count(merged_data):
    assert merged_data.width == 72, f"Looking for 72 columns, got {merged_data.width}."


# Check that the neighbourhoods are unique (i.e., no duplicates)
# [https://docs.pola.rs/api/python/stable/reference/series/api/polars.Series.n_unique.html]
def test_unique_neighbourhoods(merged_data):
    unique_names = merged_data.select(pl.col("neighbourhood").n_unique()).item()
    assert (
        unique_names == merged_data.height
    ), "Neighbourhood names are not unique, check for duplicates"


# Check for missing values (sum of the null counts across all columns should be zero)
# [https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.null_count.html]
def test_no_missing(merged_data):
    total_nulls = merged_data.null_count().to_series().sum()
    assert total_nulls == 0, f"Found {total_nulls} missing values"


# Check that all analysis columns have the correct data type (compared data to the map; e.g., integers for counts, floats for proportion/rates)
# Polars DFs have schemas (.schema) that map column names to data types
# [https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.schema.html]
def test_variable_types(merged_data):
    expected_types = {
        "neighbourhood": pl.Utf8,  # character/string data
        "one_parent_families": pl.Int64,  # integer count
        "two_parent_families": pl.Int64,
        "prop_single_parent": pl.Float64,  # proportion (float between 0 and 1)
        "prop_single_parent": pl.Float64,  # proportion (0–1)
        "median_income": pl.Float64,  # continuous
        "unemployment_rate": pl.Float64,  # proportion
        "total_education": pl.Float64,  # count
        "bachelors_or_higher": pl.Float64,  # count
        "education_rate": pl.Float64,  # proportion (0–1)
    }

    # Need to loop through each column in the expected_types dictionary + add the year
    # Generate a list of crime types
    crime_types = ["assault", "robbery", "breakenter", "homicide", "shooting"]

    # Range of years to check (2019-2024)
    years = range(2019, 2025)
    # For each crime type and year, dynamically generate two expected column names (count, rate)
    for crime in crime_types:
        for year in years:
            expected_types[f"{crime}_{year}"] = pl.Int64  # counts are integers
            expected_types[f"{crime}_rate_{year}"] = (
                pl.Float64
            )  # rates are floating-point numbers

    # Loop through each column in the expected_types dictionary
    for column, expected_type in expected_types.items():
        actual_type = merged_data.schema.get(
            column
        )  # check the actual type from the Polars DF schema
        assert (
            actual_type == expected_type
        ), f"{column} has type {actual_type}, expected {expected_type}"  # signal an assertion error if mismatched


# Check that the crime incidents = 0 or greater
# [https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.min.html]
def test_non_negative_counts(merged_data):
    for crime in ["assault", "robbery", "breakenter", "homicide", "shooting"]:
        for year in range(2019, 2025):
            column = f"{crime}_{year}"
            min = merged_data.select(pl.col(column).min()).item()
            assert min >= 0, f"{column} has negative values (min = {min})"


# Check that the crime rates are actually plausible (again, guesstimating 0-2500 per 100K people)
def test_plausible_rates(merged_data):
    for crime in ["assault", "robbery", "breakenter", "homicide", "shooting"]:
        for year in range(2019, 2025):
            column = f"{crime}_rate_{year}"
            min_value, max_value = merged_data.select(
                pl.col(column).min().alias("min"), pl.col(column).max().alias("max")
            ).row(0)
            assert 0 <= min_value < 10_000, f"{column} min {min_value} out of range"
            assert 0 <= max_value < 10_000, f"{column} max {max_value} out of range"


# Check that the single-parent family proportions fit between the bounds in the real data (~0.05, 0.55)
def test_single_parent_prop(merged_data):
    single_parent_min = merged_data.select(pl.col("prop_single_parent").min()).item()
    single_parent_max = merged_data.select(pl.col("prop_single_parent").max()).item()
    assert (
        single_parent_min >= 0.05
    ), f"Single-parent proportion {single_parent_min} is below minimum (0.05)"
    assert (
        single_parent_max <= 0.55
    ), f"Single-parent proportion {single_parent_max} is above maximum (0.55)"
