#### Preamble ####
# Purpose: Downloads and saves Toronto neighbhourhood profile and crime data from Open Data Toronto
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

#### Download xlsx data (https://docs.pola.rs/api/python/stable/reference/api/polars.read_excel.html) ####
# URL Neighbhourhood Profiles xlsx file
url_2= "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/6e19a90f-971c-46b3-852c-0c48c436d1fc/resource/19d4a806-7385-4889-acf2-256f1e079060/download/neighbourhood-profiles-2021-158-model.xlsx"

# Read the xlsx into a Polars DataFrame
df_profiles = pl.read_excel(url_2)

# Save the raw data
df_profiles.write_excel("data/01-raw_data/neighbhourhood_profiles.xlsx")