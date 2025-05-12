#### Preamble ####
# Purpose: Simulates a dataset of 2021 Toronto Neighbhourhood Crime Data (aggregated by Ward), 
  # merged with Census data on single/dual-family households.
# Author: Mike Cowan
# Date: 9 May 2025
# Contact: m.cowan@mail.utoronto.ca
# License: MIT
# Pre-requisites: 
  # - `polars` must be installed (pip install polars)
  # - `numpy` must be installed (pip install numpy)


#### Workspace setup ####
import polars as pl
import numpy as np
np.random.seed(853)


#### Simulate data ####
# Toronto Neighbourhoods (2021)
neighbhourhoods = [
    "Etobicoke North", "Etobicoke Centre", "Etobicoke-Lakeshore", "Parkdale-High Park",
    "York South-Weston", "York Centre", "Humber River-Black Creek", "Eglinton-Lawrence",
    "Davenport", "Spadina-Fort York", "University-Rosedale", "Toronto-St. Paul’s",
    "Toronto Centre", "Toronto-Danforth", "Don Valley West", "Don Valley East",
    "Don Valley North", "Willowdale", "Beaches-East York", "Scarborough Southwest",
    "Scarborough Centre", "Scarborough-Agincourt", "Scarborough North", "Scarborough-Guildwood",
    "Scarborough-Rouge Park"
]

# Crime rates
parties = ["Labor", "Liberal", "Greens", "National", "Other"]

# Probabilities for state and party distribution
state_probs = [0.25, 0.25, 0.15, 0.1, 0.1, 0.1, 0.025, 0.025]
party_probs = [0.40, 0.40, 0.05, 0.1, 0.05]

# Generate the data using numpy and polars
divisions = [f"Division {i}" for i in range(1, 152)]
states_sampled = np.random.choice(states, size=151, replace=True, p=state_probs)
parties_sampled = np.random.choice(parties, size=151, replace=True, p=party_probs)

# Create a polars DataFrame
analysis_data = pl.DataFrame({
    "division": divisions,
    "state": states_sampled,
    "party": parties_sampled
})


#### Save data ####
analysis_data.write_csv("data/00-simulated_data/simulated_data.csv")
