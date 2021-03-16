"""
Header
"""

import pandas as pd
import geopandas as gpd
import numpy as np

import data_manager

# world_vaccinations
# world_population

STATE_IDENTIFIERS = 'us_state_identifiers.csv'

def get_identifier_mapping(csv_ids):
    """
    Method Description
    """

    return {item[0]: item[1] for item in csv_ids.to_dict('split')['data']}

def process_world_data(data):
    """
    Method Description
    """

    # Load world data on new COVID cases and daily vaccinations
    world_cases = data['world_covid_data'][['location', 'date', 'iso_code', 'new_cases']]
    world_vaccinations = data['world_covid_vaccinations'][['location', 'date', 'iso_code', 'daily_vaccinations']]

    # Merge and return data
    return pd.merge(world_cases, world_vaccinations,  how='left', on=['location', 'date', 'iso_code'])

def process_us_data(data, state_ids):
    """
    Method Description
    """

    # Get US state two-letter ID mappings
    state_ids_mapping = get_identifier_mapping(state_ids)

    # Load US state data on new COVID cases and daily vaccinations
    us_cases = data['us_covid_data'][['state', 'submission_date', 'new_case']]
    us_vaccinations = data['us_covid_vaccinations'][['location', 'date', 'daily_vaccinations']].copy()
    us_vaccinations['location'].replace(state_ids_mapping, inplace = True)
    us_vaccinations.rename(columns = {'location': 'state', 'date': 'submission_date'}, inplace = True)

    # Merge and filter data to only include required rows and 50 mainland US states + DC
    us_data = pd.merge(us_cases, us_vaccinations,  how='outer', on=['state', 'submission_date'])
    us_data = us_data[['state', 'submission_date', 'new_case', 'daily_vaccinations']]
    us_data = us_data[us_data['state'].isin(state_ids['Identifier'])]

    # Get real datetimes for data
    us_data['submission_date'] = pd.to_datetime(us_data['submission_date'], infer_datetime_format = True)

    return us_data


def process_us_age_ethnicity_data(data, state_ids):
    """
    Method Description
    """

    # Get US state two-letter ID mappings
    state_ids_mapping = get_identifier_mapping(state_ids)

    # Load US state data on deaths due to COVID by ethnicity, filter to contain only 50 mainland US states + DC
    us_ethnicity_deaths = data['us_covid_ethnicity_deaths'][['Date', 'State', 'Deaths_Total', 'Deaths_White', 'Deaths_Black', 'Deaths_Latinx', 'Deaths_Asian', 'Deaths_AIAN', 'Deaths_NHPI', 'Deaths_Multiracial', 'Deaths_Other', 'Deaths_Unknown']].copy()
    us_ethnicity_deaths['Date'] = pd.to_datetime(us_ethnicity_deaths['Date'], format='%Y%m%d')
    us_ethnicity_deaths = us_ethnicity_deaths[us_ethnicity_deaths['State'].isin(state_ids['Identifier'])]

    # Load US state data on deaths due to COVID by age and filter out separate male/female data
    us_age_deaths = data['us_covid_age_deaths'][['Age Group', 'COVID-19 Deaths', 'Sex']].copy()
    us_age_deaths = us_age_deaths[us_age_deaths['Sex'] == 'All Sexes'][['Age Group', 'COVID-19 Deaths']]

    # Arrange data by age group
    us_age_deaths = us_age_deaths.pivot(columns = 'Age Group', values = 'COVID-19 Deaths')
    us_age_deaths = us_age_deaths.drop(columns = 'All Ages')

    # Add additional date and state columns to age death data
    us_age_deaths.insert(0, column = 'Date', value = data['us_covid_age_deaths']['End Date'])
    us_age_deaths.insert(1, column = 'State', value = data['us_covid_age_deaths']['State'])
    us_age_deaths['Date'] = pd.to_datetime(us_age_deaths['Date'], format='%m/%d/%Y')

    # Filter age data to only contain the 50 mainland US states + DC, collapse by day and state
    us_age_deaths = us_age_deaths[us_age_deaths['State'].isin(state_ids['Name'])]
    us_age_deaths['State'].replace(state_ids_mapping, inplace = True)
    us_age_deaths = us_age_deaths.groupby(['Date', 'State']).mean()

    # Merge ethnicity and age death data
    us_age_ethnicity_data = pd.merge_ordered(us_ethnicity_deaths, us_age_deaths,  how='outer', on=['Date', 'State'])

    return us_age_ethnicity_data


def main():
    """
    Method Description
    """

    datasets = data_manager.get_dataset_info()
    data_manager.update_datasets(datasets)
    data = data_manager.retrieve_datasets(datasets)

    world_data = process_world_data(data)

    state_ids = pd.read_csv(STATE_IDENTIFIERS)
    us_data = process_us_data(data, state_ids)
    us_age_ethnicity_deaths_data = process_us_age_ethnicity_data(data, state_ids)
    us_all_data = pd.merge_ordered(us_data, us_age_ethnicity_deaths_data,  how='outer', left_on=['submission_date', 'state'], right_on=['Date', 'State'])
    us_all_data = us_all_data.drop(columns = ['Date', 'State'])

    world_map = data['world_countries_map']
    us_map = data['us_states_map']

    print(world_data)
    print(world_data.columns)
    print(us_data)
    print(us_data.columns)
    print(us_age_ethnicity_deaths_data)
    print(us_age_ethnicity_deaths_data.columns)
    print(us_all_data)
    print(us_all_data.columns)
    print(world_map)
    print(us_map)
    

if __name__ == "__main__":
    main()
