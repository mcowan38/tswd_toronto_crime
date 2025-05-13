#### Preamble ####
# Purpose: Cleans the raw neighbourhood crime data.
# Author: Michael Cowan
# Date: 13 May 2025
# Contact: m.cowan@mail.utoronto.ca
# License: MIT
# Pre-requisites: [...UPDATE THIS...]
# Any other information needed? [...UPDATE THIS...]

#### Workspace setup ####
import polars as pl
import numpy as np

#### Clean neighbourhood crime data ####
# Neighbourhood crime data
crime_df = pl.read_csv("data/01-raw_data/neighbourhood_crime.csv")

# Select columns of interest
# (https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.select.html#polars.DataFrame.select)
crime_2021 = crime_df.select(
    "AREA_NAME",  # neighbourhoods
    "ASSAULT_RATE_2021",
    "ASSAULT_2021",
    "BREAKENTER_2021",
    "BREAKENTER_RATE_2021",
    "HOMICIDE_2021",
    "HOMICIDE_RATE_2021",
    "ROBBERY_2021",
    "ROBBERY_RATE_2021",
    "SHOOTING_2021",
    "SHOOTING_RATE_2021",
)

# Rename columns
crime_2021 = crime_2021.rename(
    {
        "AREA_NAME": "neighbourhood",
        "ASSAULT_2021": "assault_count",
        "ASSAULT_RATE_2021": "assault_rate",
        "BREAKENTER_2021": "break-enter_count",
        "BREAKENTER_RATE_2021": "break-enter_rate",
        "HOMICIDE_2021": "homicide_count",
        "HOMICIDE_RATE_2021": "homicide_rate",
        "ROBBERY_2021": "robbery_count",
        "ROBBERY_RATE_2021": "robbery_rate",
        "SHOOTING_2021": "shooting_count",
        "SHOOTING_RATE_2021": "shooting_rate",
    }
)

#### Save data ####
crime_2021.write_csv("data/02-analysis_data/analysis_data_crime.csv")
