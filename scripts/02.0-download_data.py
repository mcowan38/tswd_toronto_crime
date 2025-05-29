#### Preamble ####
# Purpose: Downloads and saves Toronto neighbourhood profile and crime data from Open Data Toronto's CKAN
# Author: Mike Cowan
# Date: 19 May 2025
# Contact: m.cowan@mail.utoronto.ca
# License: MIT
# Pre-requisites:
# - `requests` must be installed (pip install requests)

#### Workspace setup ####
import requests


#### MAIN FUNCTION ####
def main():
    print("Downloading datasets.")

    #### 02.0-download_data.py ####
    #### Download data ####
    # Toronto Open Data is stored in a CKAN instance. It's APIs are documented here:
    # [https://docs.ckan.org/en/latest/api/]

    # To hit our API, you'll be making requests to:
    base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca"

    # Datasets are called "packages". Each package can contain many "resources"
    # To retrieve the metadata for this package and its resources, use the package name in this page's URL:
    url = base_url + "/api/3/action/package_show"

    # Crime package
    params_crime = {"id": "neighbourhood-crime-rates"}
    package_crime = requests.get(url, params=params_crime).json()

    # Profile package
    params_profile = {"id": "neighbourhood-profiles"}
    package_profile = requests.get(url, params=params_profile).json()

    # To get resource data for crime:
    for c_idx, c_resource in enumerate(package_crime["result"]["resources"]):
        # for datastore_active resources:
        if c_resource["datastore_active"]:
            # To get all records in CSV format:
            c_url = base_url + "/datastore/dump/" + c_resource["id"]
            c_resource_dump_data = requests.get(c_url).text
            #### Save string data to CSV file ####
            # [https://docs.python.org/3/library/functions.html#open]
            with open(
                "data/01-raw_data/neighbourhood_crime.csv", "w", encoding="utf-8"
            ) as f:
                f.write(c_resource_dump_data)

    # To get resource data for profiles:
    for p_idx, p_resource in enumerate(package_profile["result"]["resources"]):
        # To get all records in XLSX format:
        if p_resource.get("format", "").lower() == "xlsx":
            p_url = p_resource["url"]
            p_resource_dump_data = requests.get(p_url).content
            #### Save bytes data to XLSX file ####
            # [https://docs.python.org/3/library/functions.html#open]
            with open("data/01-raw_data/neighbourhood_profiles.xlsx", "wb") as f:
                f.write(p_resource_dump_data)


#### ENTRY POINT ####
if __name__ == "__main__":
    main()
    print("Data downloaded successfully.")
