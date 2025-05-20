#### Preamble ####
# Purpose: Simulates a dataset of 2021-2024 Toronto neighbourhood crime data merged with Census data on single/dual-family households.
# Author: Mike Cowan
# Date: 19 May 2025
# Contact: m.cowan@mail.utoronto.ca
# License: MIT
# Pre-requisites:
# - `polars` must be installed (pip install polars)
# - `numpy` must be installed (pip install numpy)

#### Workspace setup ####
import polars as pl
import numpy as np
import pytest

# Create NumPy rng generator
# [https://numpy.org/doc/stable/reference/random/generator.html#numpy.random.Generator]
rng = np.random.default_rng(838)

#### Simulate Census Data ####
# 158 Toronto neighbourhoods
neighbourhoods = [f"neighbourhood {i}" for i in range(1, 159)]
years = [2019, 2020, 2021, 2022, 2023, 2024]

# Total families per neighbourhood using the min-max from the real dataset
# e.g., University = lowest, Glenfield-Jane Heights = highest
# [https://tellingstorieswithdata.com/21-python_essentials.html#python-vs-code-and-uv]
total_families = rng.integers(low=600, high=4290, size=158)

# Proportion of single-parent families (Beta distribution for proportions, bounded from ~15-55% based on the real dataset)
prop_single_parent = np.clip(
    rng.beta(4, 18, size=158),  # α=4, β=18 (mean ~0.18)
    0.15,  # force lower bound at 15%
    0.55,  # force upper bound at 55%
)
# Family counts
single_parent_families = (prop_single_parent * total_families).round().astype(int)
two_parent_families = total_families - single_parent_families

# Total population per neighbourhood using the min-max from the real dataset
total_population = rng.integers(low=6260, high=33300, size=158)

#### Simulate Crime Data ####
# Crime counts (Poisson draws = counts) guesstimating baselines (more common crimes have higher rates)
# e.g., crime_count = rng.poisson(X crimes per 1 000 people scaled to neighbourhood size)
# [https://www.slingacademy.com/article/numpy-understanding-random-generator-poisson-method-4-examples/]
assault = rng.poisson(8 * (total_population / 1000))
robbery = rng.poisson(4 * (total_population / 1000))
breakenter = rng.poisson(2 * (total_population / 1000))
homicide = rng.poisson(0.025 * (total_population / 1000))
shooting = rng.poisson(0.075 * (total_population / 1000))

# Convert to crime rates (standard is per 100K persons)
assault_rate = assault / total_population * 100000
robbery_rate = robbery / total_population * 100000
breakenter_rate = breakenter / total_population * 100000
homicide_rate = homicide / total_population * 100000
shooting_rate = shooting / total_population * 100000


# Convert to DF
simulated_df = pl.DataFrame(
    {
        "neighbourhood": neighbourhoods,
        "total_families": total_families,
        "single_parent_families": single_parent_families,
        "two_parent_families": two_parent_families,
        "prop_single_parent": prop_single_parent,
        "assault": assault,
        "robbery": robbery,
        "breakenter": breakenter,
        "homicide": homicide,
        "shooting": shooting,
        "assault_rate": assault_rate,
        "robbery_rate": robbery_rate,
        "breakenter_rate": breakenter_rate,
        "homicide_rate": homicide_rate,
        "shooting_rate": shooting_rate,
    }
)

#### Save data ####
simulated_df.write_csv("data/00-simulated_data/simulated_data.csv")
