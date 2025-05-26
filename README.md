# Neighbourhood Crime and SES [Work in Progress]

## Overview

This repo tests the hypothesis that Toronto neighbourhoods with a higher proportion of single-parent households tend to experience higher rates of serious crime (i.e., assault, break and enter, homicide, robbery, and shooting incidents). The analysis, conducted in Python, utilizes the City of Toronto's neighbourhood crime data and census data from 2021.


## File Structure

The repo is structured as:

-   `data/00-simulated_data` contains simulated data used to test the analysis pipeline.
-   `data/01-raw_data` contains the raw data as obtained from City of Toronto Open Data (https://open.toronto.ca/).
-   `data/02-analysis_data` contains the cleaned datasets that were constructed.
-   `models` contains fitted models (k-means clustering). 
-   `other` contains relevant literature and sketches.
-   `paper` contains the files used to generate the paper, including the Quarto document and reference bibliography file, as well as the PDF of the paper. 
-   `scripts` contains the Python scripts used to simulate, download, clean, merge, test, and model the data.


## Statement on LLM usage

The Qodo Gen extension (AI auto-complete for VScode) was enabled during initial generation of the virtual environment prior to the initial commit. In addition, 04-mini-high assisted in coding troubleshooting in the following scripts:
- 03.1-clean_profile_data.py
- 06.0-eda_neighbourhood_clusters.py
- 06.1-eda_crime_clusters.py