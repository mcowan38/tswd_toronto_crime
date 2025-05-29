#### Preamble ####
# Purpose: Cleans the raw neighbourhood crime data.
# Author: Mike Cowan
# Date: 19 May 2025
# Contact: m.cowan@mail.utoronto.ca
# License: MIT
# Pre-requisites:
# - `polars` must be installed (pip install polars)

#### Workspace setup ####
import polars as pl


#### MAIN FUNCTION ####
def main():
    print("Cleaning neighbourhood crime data.")

    #### 03.0-clean_crime_data.py ####
    #### Load and clean neighbourhood crime data ####
    # Neighbourhood crime data
    crime_df = pl.read_csv("data/01-raw_data/neighbourhood_crime.csv")

    # Select columns of interest
    # [https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.select.html#polars.DataFrame.select]
    crime_df = crime_df.select(
        "AREA_NAME",  # neighbourhoods
        "ASSAULT_2019",
        "ASSAULT_RATE_2019",
        "ASSAULT_2020",
        "ASSAULT_RATE_2020",
        "ASSAULT_2021",
        "ASSAULT_RATE_2021",
        "ASSAULT_2022",
        "ASSAULT_RATE_2022",
        "ASSAULT_2023",
        "ASSAULT_RATE_2023",
        "ASSAULT_2024",
        "ASSAULT_RATE_2024",
        "BREAKENTER_2019",
        "BREAKENTER_RATE_2019",
        "BREAKENTER_2020",
        "BREAKENTER_RATE_2020",
        "BREAKENTER_2021",
        "BREAKENTER_RATE_2021",
        "BREAKENTER_2022",
        "BREAKENTER_RATE_2022",
        "BREAKENTER_2023",
        "BREAKENTER_RATE_2023",
        "BREAKENTER_2024",
        "BREAKENTER_RATE_2024",
        "HOMICIDE_2019",
        "HOMICIDE_RATE_2019",
        "HOMICIDE_2020",
        "HOMICIDE_RATE_2020",
        "HOMICIDE_2021",
        "HOMICIDE_RATE_2021",
        "HOMICIDE_2022",
        "HOMICIDE_RATE_2022",
        "HOMICIDE_2023",
        "HOMICIDE_RATE_2023",
        "HOMICIDE_2024",
        "HOMICIDE_RATE_2024",
        "ROBBERY_2019",
        "ROBBERY_RATE_2019",
        "ROBBERY_2020",
        "ROBBERY_RATE_2020",
        "ROBBERY_2021",
        "ROBBERY_RATE_2021",
        "ROBBERY_2022",
        "ROBBERY_RATE_2022",
        "ROBBERY_2023",
        "ROBBERY_RATE_2023",
        "ROBBERY_2024",
        "ROBBERY_RATE_2024",
        "SHOOTING_2019",
        "SHOOTING_RATE_2019",
        "SHOOTING_2020",
        "SHOOTING_RATE_2020",
        "SHOOTING_2021",
        "SHOOTING_RATE_2021",
        "SHOOTING_2022",
        "SHOOTING_RATE_2022",
        "SHOOTING_2023",
        "SHOOTING_RATE_2023",
        "SHOOTING_2024",
        "SHOOTING_RATE_2024",
    )

    # Rename neighbourhood column
    clean_df = crime_df.rename({"AREA_NAME": "neighbourhood"})

    # Normalize the text in neighbourhood so it matches the profile side
    clean_df = clean_df.with_columns(
        pl.col("neighbourhood")
        .str.normalize(form="NFKC")
        .str.strip_chars(" ")  # strip leading/trailing spaces
        .str.replace_all("`", "'")  # standardize apostrophes
        .str.replace_all(r"\s+", "-")  # spaces become dashes
        .str.replace_all(r"\.", "")  # drop every period
        .str.replace_all(r"\s+", "-")  # space become dashes again
        .str.to_lowercase()  # lowercase
    )

    # Fill missing values in the rate columns with 0.0
    rate_cols = [c for c in clean_df.columns if "_RATE_" in c]
    clean_df = clean_df.with_columns(
        [
            pl.col(c).fill_null(0.0).alias(c) for c in rate_cols
        ]  # replace NA with true zeros
    )

    # Lowercase all column names so joins/tests don't break later
    clean_df = clean_df.rename({c: c.lower() for c in clean_df.columns})

    #### Save data ####
    clean_df.write_csv("data/02-analysis_data/00-analysis_data_crime.csv")


#### ENTRY POINT ####
if __name__ == "__main__":
    main()
    print(
        "Neighbourhood crime data cleaned and saved to: data/02-analysis_data/00-analysis_data_crime.csv"
    )
