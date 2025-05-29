#### Workspace setup ####
import polars as pl
import itertools  # for crime-year pairs
from pathlib import Path


#### MAIN FUNCTION ####
def main():
    print("Generating crime trends by neighbourhood clusters (2019–2024).")

    #### 06.0-table_crime_clusters.py ####
    #### Load data ####
    merged_data = pl.read_csv("data/02-analysis_data/02-analysis_data_merged.csv")

    # Set parameters
    cluster_col = (
        "opportunity_index"  # SES cluster label (0 = High, 1 = Medium, 2 = Low)
    )
    crime_types = ["assault", "robbery", "breakenter", "shooting"]  # crime categories
    years = list(range(2019, 2025))  # inclusive year range

    # Collect yearly summaries for each crime type and cluster
    summaries = []
    for crime, year in itertools.product(crime_types, years):
        col_name = f"{crime}_rate_{year}"
        if col_name not in merged_data.columns:
            continue  # skip if rate column is missing

        avg_rate = (
            merged_data.select([cluster_col, col_name])
            .group_by(cluster_col)
            .agg(pl.mean(col_name).alias("avg_rate"))
            .with_columns([pl.lit(crime).alias("crime"), pl.lit(year).alias("year")])
        )
        summaries.append(avg_rate)

    # Combine into long format DF
    all_rates = pl.concat(summaries)

    #### Pivot wider: one row per (crime, year), columns = clusters ####
    wide_df = all_rates.pivot(
        index=["crime", "year"], on=cluster_col, values="avg_rate"
    ).sort(["crime", "year"])

    #### Compute year-to-year percent change for each consecutive year ####
    cluster_cols = [c for c in wide_df.columns if c not in ["crime", "year"]]
    pct_change_exprs = []
    for col in cluster_cols:
        for prev_year, curr_year in zip(years[:-1], years[1:]):
            pct_name = f"{col}_pct_{prev_year}_{curr_year}"
            expr = (
                pl.when(pl.col("year") == curr_year)
                .then(
                    (
                        (pl.col(col) - pl.col(col).shift(1).over("crime"))
                        / pl.col(col).shift(1).over("crime")
                        * 100
                    ).round(1)
                )
                .alias(pct_name)
            )
            pct_change_exprs.append(expr)
    wide_df = wide_df.with_columns(pct_change_exprs)

    #### Save to CSV ####
    Path("data/02-analysis_data").mkdir(parents=True, exist_ok=True)
    wide_df.write_csv("data/02-analysis_data/04-cluster_crime_rates.csv")

    #### Separate Tables by Crime ####
    cluster_labels = ["Low Opportunity", "Medium Opportunity", "High Opportunity"]
    years = list(range(2019, 2025))
    crime_types = ["assault", "robbery", "breakenter", "shooting"]

    #### Separate Tables by Crime ####
    cluster_labels = ["Low Opportunity", "Medium Opportunity", "High Opportunity"]
    years = list(range(2019, 2025))
    crime_types = ["assault", "robbery", "breakenter", "shooting"]

    for crime in crime_types:
        records = []
        for y in years:
            row = wide_df.filter((pl.col("crime") == crime) & (pl.col("year") == y))
            if row.is_empty():
                continue
            data = row.to_dicts()[0]

            rec = {"Year": y}
            for label in cluster_labels:
                rate = data[label]
                if y == 2019:
                    # 2019: just show the base rate
                    rec[label] = f"{rate:.1f}"
                else:
                    pct = data[f"{label}_pct_{y-1}_{y}"]
                    sign = "+" if pct >= 0 else ""
                    rec[label] = f"{rate:.1f} ({sign}{pct:.1f})"
            records.append(rec)

        table = pl.DataFrame(records).rename(
            {
                "Low Opportunity": "Low",
                "Medium Opportunity": "Med",
                "High Opportunity": "High",
            }
        )

        # Display header and table
        print(f"### {crime.title()} Rate Change")
        print(table)

        # Save each crime to its own CSV
        Path("data/03-table_data").mkdir(parents=True, exist_ok=True)
        table.write_csv(f"data/03-table_data/{crime}_rate_change.csv")


#### ENTRY POINT ####
if __name__ == "__main__":
    main()
    print("Crime trends by neighbourhood clusters (2019–2024) have been generated.")
