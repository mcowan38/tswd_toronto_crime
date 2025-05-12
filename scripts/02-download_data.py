#### Preamble ####
# Purpose: Downloads and saves the data from Open Data Toronto
# Author: Michael Cowan
# Date: 9 May 2024
# Contact: m.cowan@mail.utoronto.ca
# License: MIT
# Pre-requisites: [...UPDATE THIS...]
# Any other information needed? [...UPDATE THIS...]


#### Workspace setup ####
import polars as pl
import numpy as np

#### Download CSV data ####
# URL crime CSV file
url_1= "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/neighbourhood-crime-rates/resource/02898503-a367-4221-9e74-7addb260d110/download/neighbourhood-crime-rates%20-%204326.csv"

# Read the CSV into a Polars DataFrame
df_crime = pl.read_csv(url_1)

# Save the raw data
df_crime.write_csv("data/01-raw_data/neighbhourhood_crime.csv")

#### Download 1st xlsx data (https://docs.pola.rs/api/python/stable/reference/api/polars.read_excel.html) ####
# URL Ward Name/Numbers xlsx file
url_2= "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/6678e1a6-d25f-4dff-b2b7-aa8f042bc2eb/resource/ea4cc466-bd4d-40c6-a616-7abfa9d7398f/download/25-WardNames-Numbers.xlsx"

# Read the xlsx into a Polars DataFrame
df_ward_name = pl.read_excel(url_2)

# Save the raw data
df_ward_name.write_excel("data/01-raw_data/ward_names.xlsx")

#### Download 2nd xlsx data (https://docs.pola.rs/api/python/stable/reference/api/polars.read_excel.html) ####
# URL Ward Profile xlsx file
url_3= "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/6678e1a6-d25f-4dff-b2b7-aa8f042bc2eb/resource/16a31e1d-b4d9-4cf0-b5b3-2e3937cb4121/download/2023-WardProfiles-2011-2021-CensusData.xlsx"

# Read the xlsx into a Polars DataFrame
df_ward_census = pl.read_excel(url_3)

# Save the raw data
df_ward_census.write_excel("data/01-raw_data/ward_census.xlsx")