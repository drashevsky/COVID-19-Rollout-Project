"""
Daniel Rashevsky
CSE 163 AE
This file processes all downloaded data into a format used by data analysis to track COVID death, vaccination, and case rates
"""

import pandas as pd
import geopandas as gpd
import numpy as np

import data_manager

WORLD_IDENTIFIERS = "world_country_identifiers.csv"
STATE_IDENTIFIERS = "us_state_identifiers.csv"
TARGET_POP_YEAR = 2020
WORLD_POP_VARIANT = "Medium"


def consolidate_world_data(data):
    """
    Return final combined COVID dataset for the world, given a set of raw datasets
    """

    # Get country identifiers, map two letter to three letter ISO codes
    world_ids = pd.read_csv(WORLD_IDENTIFIERS)
    world_ids_mapping = get_identifier_mapping(world_ids)

    print("Processing world COVID case and vaccination data...")

    # Merge country case and vaccination data
    world_data = process_world_data(data)

    print("Merging world data with geospatial map...")

    # Merge consolidated dataset with country map data
    world_map = data["world_countries_map"]
    world_map["ISO"].replace(world_ids_mapping, inplace=True)
    world_data = merge_geographic_data(world_data, world_map, "iso_code", "ISO")
    world_data = world_data.drop(columns="ISO")

    return world_data


def consolidate_us_data(data):
    """
    Return final combined COVID dataset for the US, given a set of raw datasets
    """

    # Get state identifiers mapping state names to their postal codes
    state_ids = pd.read_csv(STATE_IDENTIFIERS)

    print("Processing US COVID case and vaccination data...")

    # Merge state case and vaccination data
    us_data = process_us_data(data, state_ids)

    print("Processing US death data by age and ethnicity...")

    # Merge death data for age and ethnicity by state
    us_age_ethnicity_deaths_data = process_us_age_ethnicity_data(data, state_ids)

    # Merge case, vaccination, and age/ethnicity data together
    us_all_data = pd.merge_ordered(
        us_data,
        us_age_ethnicity_deaths_data,
        how="outer",
        left_on=["submission_date", "state"],
        right_on=["Date", "State"],
    )
    us_all_data = us_all_data.drop(columns=["Date", "State"])

    print("Merging US data with geospatial map...")

    # Merge consolidated dataset with state map data
    us_map = data["us_states_map"]
    us_all_data = merge_geographic_data(us_all_data, us_map, "state", "STATE")
    us_all_data = us_all_data.drop(columns="STATE")

    return us_all_data


def process_world_data(data):
    """
    Merge several raw world datasets into a single one
    """

    # Load world data on new COVID cases and daily vaccinations
    world_cases = data["world_covid_data"][
        ["location", "date", "iso_code", "new_cases"]
    ]
    world_vaccinations = data["world_covid_vaccinations"][
        ["location", "date", "iso_code", "daily_vaccinations"]
    ]

    # Merge and return data
    return pd.merge(
        world_cases, world_vaccinations, how="left", on=["location", "date", "iso_code"]
    )


def process_us_data(data, state_ids):
    """
    Merge several raw US datasets into a single one
    """

    # Get US state two-letter ID mappings
    state_ids_mapping = get_identifier_mapping(state_ids)

    # Load US state data on new COVID cases and daily vaccinations
    us_cases = data["us_covid_data"][["state", "submission_date", "new_case"]]
    us_vaccinations = data["us_covid_vaccinations"][
        ["location", "date", "daily_vaccinations"]
    ].copy()
    us_vaccinations["location"].replace(state_ids_mapping, inplace=True)
    us_vaccinations.rename(
        columns={"location": "state", "date": "submission_date"}, inplace=True
    )

    # Merge and filter data to only include required rows and 50 mainland US states + DC
    us_data = pd.merge(
        us_cases, us_vaccinations, how="outer", on=["state", "submission_date"]
    )
    us_data = us_data[["state", "submission_date", "new_case", "daily_vaccinations"]]
    us_data = us_data[us_data["state"].isin(state_ids["Identifier"])]

    # Get real datetimes for data
    us_data["submission_date"] = pd.to_datetime(
        us_data["submission_date"], infer_datetime_format=True
    )

    return us_data


def process_us_age_ethnicity_data(data, state_ids):
    """
    Merge several raw US age and ethnicity death rate datasets into a single one
    """

    # Get US state two-letter ID mappings
    state_ids_mapping = get_identifier_mapping(state_ids)

    # Load US state data on deaths due to COVID by ethnicity, filter to contain only 50 mainland US states + DC
    us_ethnicity_deaths = data["us_covid_ethnicity_deaths"][
        [
            "Date",
            "State",
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
        ]
    ].copy()
    us_ethnicity_deaths["Date"] = pd.to_datetime(
        us_ethnicity_deaths["Date"], format="%Y%m%d"
    )
    us_ethnicity_deaths = us_ethnicity_deaths[
        us_ethnicity_deaths["State"].isin(state_ids["Identifier"])
    ]

    # Load US state data on deaths due to COVID by age and filter out separate male/female data
    us_age_deaths = data["us_covid_age_deaths"][
        ["Age Group", "COVID-19 Deaths", "Sex"]
    ].copy()
    us_age_deaths = us_age_deaths[us_age_deaths["Sex"] == "All Sexes"][
        ["Age Group", "COVID-19 Deaths"]
    ]

    # Arrange data by age group
    us_age_deaths = us_age_deaths.pivot(columns="Age Group", values="COVID-19 Deaths")
    us_age_deaths = us_age_deaths.drop(columns="All Ages")

    # Add additional date and state columns to age death data
    us_age_deaths.insert(
        0, column="Date", value=data["us_covid_age_deaths"]["End Date"]
    )
    us_age_deaths.insert(1, column="State", value=data["us_covid_age_deaths"]["State"])
    us_age_deaths["Date"] = pd.to_datetime(us_age_deaths["Date"], format="%m/%d/%Y")

    # Filter age data to only contain the 50 mainland US states + DC, collapse by day and state
    us_age_deaths = us_age_deaths[us_age_deaths["State"].isin(state_ids["Name"])]
    us_age_deaths["State"].replace(state_ids_mapping, inplace=True)
    us_age_deaths = us_age_deaths.groupby(["Date", "State"]).mean()

    # Merge ethnicity and age death data
    us_age_ethnicity_data = pd.merge_ordered(
        us_ethnicity_deaths, us_age_deaths, how="outer", on=["Date", "State"]
    )

    return us_age_ethnicity_data


def get_world_pop_data(data):
    """
    Process and return world population data in an acceptable format, given a raw world population dataset
    """

    print("Retrieving world population data...")

    # Load and filter world population data
    world_pop_data = data["world_population"]
    world_pop_data = world_pop_data[
        (world_pop_data["Time"] == TARGET_POP_YEAR)
        & (world_pop_data["Variant"] == WORLD_POP_VARIANT)
    ]
    world_pop_data = world_pop_data[["Location", "Time", "PopTotal"]]
    world_pop_data["PopTotal"] *= 1000

    # Get mapping of country names to ISO codes and two-letter to three-letter ISO codes
    world_countries = data["world_covid_data"][["location", "iso_code"]]
    world_countries_mapping = get_identifier_mapping(world_countries)
    world_ids = pd.read_csv(WORLD_IDENTIFIERS)
    world_ids_mapping = get_identifier_mapping(world_ids)

    # Filter population data to include only countries in the world COVID cases dataset
    world_pop_data["Location"].replace(world_countries_mapping, inplace=True)
    world_pop_data = world_pop_data[
        world_pop_data["Location"].isin(world_ids["Identifier"])
    ]

    return world_pop_data


def get_us_pop_data(data):
    """
    Process and return US population data in an acceptable format, given a raw world population dataset
    """

    print("Retrieving US population data...")

    # Load and filter US population data
    us_pop_data = data["us_population"]
    us_pop_data = us_pop_data[["NAME", "POPESTIMATE2020"]]

    # Get US state two-letter ID mappings
    state_ids = pd.read_csv(STATE_IDENTIFIERS)
    state_ids_mapping = get_identifier_mapping(state_ids)

    # Filter population data to include only states in the mapping, change to two letter code
    us_pop_data = us_pop_data[us_pop_data["NAME"].isin(state_ids["Name"])]
    us_pop_data["NAME"].replace(state_ids_mapping, inplace=True)

    return us_pop_data


def get_identifier_mapping(csv_ids):
    """
    Return from jurisdiction name and postal/iso code data a mapping that can be used by pd.replace
    """

    return {item[0]: item[1] for item in csv_ids.to_dict("split")["data"]}


def merge_geographic_data(data, geodata, data_locations_col, geodata_locations_col):
    """
    Merge geometry data with a regular pandas dataset, return merged data
    """

    return pd.merge(
        data,
        geodata[[geodata_locations_col, "geometry"]],
        how="left",
        left_on=data_locations_col,
        right_on=geodata_locations_col,
    )


def main():
    """
    Test all methods in data_processing
    """

    datasets = data_manager.get_dataset_info()
    data_manager.update_datasets(datasets)
    data = data_manager.retrieve_datasets(datasets)

    # Test world/us data consolidation methods
    world_c_data = consolidate_world_data(data)
    us_c_data = consolidate_us_data(data)
    world_pop = get_world_pop_data(data)
    us_pop = get_us_pop_data(data)

    # Print results
    print(world_c_data)
    print(world_c_data.columns)
    print(us_c_data)
    print(us_c_data.columns)
    print(world_pop)
    print(us_pop)


if __name__ == "__main__":
    main()
