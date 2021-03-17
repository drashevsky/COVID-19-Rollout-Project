"""
Daniel Rashevsky
CSE 163 AE
This file analyzes all consolidated COVID datasets into results used by visualization
"""

import pandas as pd
import geopandas as gpd
import numpy as np

import data_manager
import data_processing

WORLD_STATS = ["new_cases", "daily_vaccinations"]
US_STATS = [
    "new_case",
    "daily_vaccinations",
    "Deaths_Total",
    "Deaths_White",
    "Deaths_Black",
    "Deaths_Latinx",
    "Deaths_Asian",
    "Deaths_AIAN",
    "Deaths_NHPI",
    "Deaths_Multiracial",
    "Deaths_Other",
    "Deaths_Unknown",
    "0-17 years",
    "1-4 years",
    "15-24 years",
    "18-29 years",
    "25-34 years",
    "30-39 years",
    "35-44 years",
    "40-49 years",
    "45-54 years",
    "5-14 years",
    "50-64 years",
    "55-64 years",
    "65-74 years",
    "75-84 years",
    "85 years and over",
    "Under 1 year",
]


def analyze_world_data(world_data, world_pop_data):
    """
    Analyzes the consolidated world and world population data, returns several smaller datasets with per capita rate calculations
    """

    print("Analyzing world data...")

    # Filter world case and vaccinations data to countries with known population
    world_data = world_data[
        world_data["iso_code"].isin(world_pop_data["Location"])
    ].copy()

    # Find per capita daily case and vaccination rates
    for index, row in world_pop_data.iterrows():
        jurisdiction = world_data[world_data["iso_code"] == row["Location"]].copy()
        jurisdiction[WORLD_STATS] /= row["PopTotal"]
        world_data[world_data["iso_code"] == row["Location"]] = jurisdiction

    # Fill empty daily case and vaccination rate cells
    filled_world_data = world_data.copy()
    filled_world_data[WORLD_STATS] = filled_world_data[WORLD_STATS].fillna(0)

    # Find average daily case and vaccination rates for all the data for each country
    average_per_cap_by_country = filled_world_data.groupby(["iso_code", "location"])[
        WORLD_STATS
    ].mean()
    average_per_cap_by_country = data_processing.merge_geographic_data(
        average_per_cap_by_country, world_data, "iso_code", "iso_code"
    )

    # Find average daily case and vaccination rates for every day we have data on across countries
    average_per_cap_by_day = filled_world_data.groupby("date")[WORLD_STATS].mean()

    return world_data, average_per_cap_by_country, average_per_cap_by_day


def analyze_us_data(us_data, us_pop_data):
    """
    Analyzes the consolidated US and US population data, returns several smaller datasets with per capita rate calculations
    """

    print("Analyzing US data...")

    # Filter US case and vaccinations data to states with known population
    us_data = us_data[us_data["state"].isin(us_pop_data["NAME"])].copy()

    # Find per capita daily case, vaccination, age-based death, and ethnicity-based death rates
    for index, row in us_pop_data.iterrows():
        jurisdiction = us_data[us_data["state"] == row["NAME"]].copy()
        jurisdiction[US_STATS] /= row["POPESTIMATE2020"]
        us_data[us_data["state"] == row["NAME"]] = jurisdiction

    # Fill empty daily case, vaccination, age-based death, and ethnicity-based death rate cells
    filled_us_data = us_data.copy()
    filled_us_data[US_STATS] = filled_us_data[US_STATS].fillna(0)

    # Find average rates for all the data for each state
    average_per_cap_by_state = filled_us_data.groupby(["state"])[US_STATS].mean()
    average_per_cap_by_state = data_processing.merge_geographic_data(
        average_per_cap_by_state, us_data, "state", "state"
    )

    # Find average rates for every day we have data on across states
    average_per_cap_by_day = filled_us_data.groupby("submission_date")[US_STATS].mean()

    return us_data, average_per_cap_by_state, average_per_cap_by_day


def main():
    """
    Tests all methods in analysis
    """

    datasets = data_manager.get_dataset_info()
    data_manager.update_datasets(datasets)
    data = data_manager.retrieve_datasets(datasets)

    # Test world analysis
    world_c_data = data_processing.consolidate_world_data(data)
    world_pop = data_processing.get_world_pop_data(data)
    print(analyze_world_data(world_c_data, world_pop))

    # Test US analysis
    us_c_data = data_processing.consolidate_us_data(data)
    us_pop = data_processing.get_us_pop_data(data)
    print(analyze_us_data(us_c_data, us_pop))


if __name__ == "__main__":
    main()
