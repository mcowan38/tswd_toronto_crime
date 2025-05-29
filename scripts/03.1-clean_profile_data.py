#### Preamble ####
# Purpose: Cleans the raw neighbourhood profile data.
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
    print("Cleaning neighbourhood profile data.")

    #### 03.1-clean_profile_data.py ####
    #### Load and clean neighbourhood profile data ####
    # Neighbourhood profile data
    profile_df = pl.read_excel("data/01-raw_data/neighbourhood_profiles.xlsx")

    # Unicode normalization, strip whitespace and replace a problem apostrophe (in Neighbourhood Name)
    # [https://sparkbyexamples.com/polars/strip-entire-polars-dataframe]
    profile_standardize = profile_df.with_columns(
        pl.col("Neighbourhood Name")
        .str.normalize(form="NFKC")
        .str.strip_chars(" ")
        .str.replace("’", "'")
        .str.replace("‘", "'")
        .str.replace("’", "'")
    )

    # Filter the specific rows of interest
    profile_filter = profile_standardize.filter(
        pl.col("Neighbourhood Name").is_in(
            [
                "Total - Persons in private households - 25% sample data",  # row 37
                "Couple-family households",  # row 235
                "One-parent-family households",  # row 238
                "Median total income of household in 2020 ($)",  # row 245
                "Unemployment rate",  # row 1972
                "Total - Highest certificate, diploma or degree for the population aged 25 to 64 years in private households - 25% sample data",  # row 2064
                "Bachelor's degree or higher",  # row 1992 and 2074 (we want the latter)
            ]
        )
        # Deal with duplicate rows (selected the latter)
        # [https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.unique.html]
    ).unique(subset="Neighbourhood Name", keep="last", maintain_order=True)

    # Need to flip the spreadsheet to merge (transpose: rows become columns and vice versa)
    # [https://sparkbyexamples.com/polars/polars-transpose-dataframe/]
    profile_transposed = profile_filter.transpose(
        include_header=True,  # bring the original column names
        header_name="neighbourhood",  # rename the header column (1st column)
        column_names=[  # rename the subsequent columns
            "total_households",  # denominator for all crime rates (per 100K)
            "two_parent_families",
            "one_parent_families",  # numerator for single-parent share (single_parent_share = one_parent_families / total_households)
            "median_income",  # control
            "unemployment_rate",  # control
            "total_education",  # numerator for education share
            "bachelors_or_higher",  # denominator for education share (education_rate = bachelors_or_higher / total_education)
        ],
    )

    # Slice redundant row (duplicate header)
    # [https://sparkbyexamples.com/polars/polars-dataframe-slice-usage-examples]
    profile_transposed = profile_transposed.slice(1)

    # Convert numeric columns back to integers and floats (set to str after transposing)
    # [https://sparkbyexamples.com/polars/polars-transpose-dataframe]
    profile_transposed = profile_transposed.with_columns(
        [
            pl.col("total_households").cast(pl.Int64),
            pl.col("two_parent_families").cast(pl.Int64),
            pl.col("one_parent_families").cast(pl.Int64),
            pl.col("median_income").cast(pl.Float64),
            pl.col("unemployment_rate").cast(pl.Float64),
            pl.col("total_education").cast(pl.Float64),
            pl.col("bachelors_or_higher").cast(pl.Float64),
        ]
    )

    # Single-parent proportion = one-parent families / (one-parent families + couple-family households)
    profile_clean = profile_transposed.with_columns(
        [
            # Single-parent proportion of all nuclear ("Census") families
            (
                pl.col("one_parent_families")
                / (pl.col("one_parent_families") + pl.col("two_parent_families"))
            ).alias("prop_single_parent"),
            # Education rate = share with bachelor’s or above among all certificate/degree holders
            (pl.col("bachelors_or_higher") / pl.col("total_education")).alias(
                "education_rate"
            ),
        ]
    )

    # Lowercase all column names so joins/tests don't break later
    profile_clean = profile_clean.rename({c: c.lower() for c in profile_clean.columns})

    # Normalize the text in neighbourhood so it matches the crime side
    profile_clean = profile_clean.with_columns(
        pl.col("neighbourhood")
        .str.normalize(form="NFKC")
        .str.strip_chars(" ")  # strip leading/trailing spaces
        .str.replace_all("`", "'")  # standardize apostrophes
        .str.replace_all(r"\s+", "-")  # spaces become dashes
        .str.replace_all(r"\.", "")  # drop every period
        .str.replace_all(r"\s+", "-")  # space become dashes again
        .str.to_lowercase()  # lowercase
        # Manually adjust specific neighbourhoods (see below)
        .str.replace_all(r"st-james", "stjames")
        .str.replace_all(r"st-clair", "stclair")
        .str.replace_all(
            r"cabbagetown-south-st-james-town", "cabbagetown-south-stjames-town"
        )
    )

    #### Save data ####
    profile_clean.write_csv("data/02-analysis_data/01-analysis_data_profiles.csv")


#### ENTRY POINT ####
if __name__ == "__main__":
    main()
    print("Neighbourhood profile data cleaned and saved.")
