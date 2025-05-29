#### Preamble ####
# Purpose: Merges the cleaned neighbourhood crime and Census profile data.
# Author: Mike Cowan
# Date: 19 May 2025
# Contact: m.cowan@mail.utoronto.ca
# License: MIT
# Pre-requisites:
# - `polars` must be installed (pip install polars)

#### Workspace setup ####
import polars as pl
import functools  # inherent to Python
import operator  # inherent to Python


#### MAIN FUNCTION ####
def main():
    print("Merging neighbourhood crime and profile data.")

    #### 04.0-merge_crime_profile.py ####
    #### Load and merge neighbourhood crime and profile data ####
    crime_df = pl.read_csv("data/02-analysis_data/00-analysis_data_crime.csv")
    profile_df = pl.read_csv("data/02-analysis_data/01-analysis_data_profiles.csv")

    # Anti-join to identify any name mismatches; "which crime names do not appear in profile_df?"
    # [https://docs.pola.rs/user-guide/transformations/joins/#semi-join]
    mismatches = crime_df.join(profile_df, on="neighbourhood", how="anti")
    print(mismatches.select("neighbourhood").unique().to_series().to_list())

    # Merge the two DFs on the neighbourhood column
    # [https://dataguymichael.substack.com/p/the-ultimate-polars-cheat-sheet-for]
    merged_df = crime_df.join(
        profile_df,
        on="neighbourhood",
        how="left",  # keep rows from right dataframe (profile_df)
    )

    # Reorder columns via select (recommended method for polars); one-parent-family households first, then two-parent families, etc.
    # [https://stackoverflow.com/questions/71353113/polars-how-to-reorder-columns-in-a-specific-order]
    clean_df = merged_df.select(
        [
            # profile columns
            "neighbourhood",
            "total_households",
            "two_parent_families",
            "one_parent_families",
            "prop_single_parent",
            "median_income",
            "unemployment_rate",
            "total_education",
            "bachelors_or_higher",
            "education_rate",
            # crime columns
            "assault_2019",
            "assault_rate_2019",
            "assault_2020",
            "assault_rate_2020",
            "assault_2021",
            "assault_rate_2021",
            "assault_2022",
            "assault_rate_2022",
            "assault_2023",
            "assault_rate_2023",
            "assault_2024",
            "assault_rate_2024",
            "breakenter_2019",
            "breakenter_rate_2019",
            "breakenter_2020",
            "breakenter_rate_2020",
            "breakenter_2021",
            "breakenter_rate_2021",
            "breakenter_2022",
            "breakenter_rate_2022",
            "breakenter_2023",
            "breakenter_rate_2023",
            "breakenter_2024",
            "breakenter_rate_2024",
            "homicide_2019",
            "homicide_rate_2019",
            "homicide_2020",
            "homicide_rate_2020",
            "homicide_2021",
            "homicide_rate_2021",
            "homicide_2022",
            "homicide_rate_2022",
            "homicide_2023",
            "homicide_rate_2023",
            "homicide_2024",
            "homicide_rate_2024",
            "robbery_2019",
            "robbery_rate_2019",
            "robbery_2020",
            "robbery_rate_2020",
            "robbery_2021",
            "robbery_rate_2021",
            "robbery_2022",
            "robbery_rate_2022",
            "robbery_2023",
            "robbery_rate_2023",
            "robbery_2024",
            "robbery_rate_2024",
            "shooting_2019",
            "shooting_rate_2019",
            "shooting_2020",
            "shooting_rate_2020",
            "shooting_2021",
            "shooting_rate_2021",
            "shooting_2022",
            "shooting_rate_2022",
            "shooting_2023",
            "shooting_rate_2023",
            "shooting_2024",
            "shooting_rate_2024",
        ]
    )

    #### Save data ####
    clean_df.write_csv("data/02-analysis_data/02-analysis_data_merged.csv")


#### ENTRY POINT ####
if __name__ == "__main__":
    main()
    print("Datasets have been merged.")
