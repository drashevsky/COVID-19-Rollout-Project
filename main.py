"""
Daniel Rashevsky
CSE 163 AE
This file downloads, processes, analyzes, and graphs data statistics about COVID-19
daily cases and vaccinations for the US and world, as well as the death rates of
different age and ethnic groups of COVID-19 in the US
"""

import pandas as pd
import geopandas as gpd
import numpy as np

import data_manager
import data_processing
import analysis
import visualization

DAILY_TRENDS_ENABLED = False


def plot_daily_trends(world_results, us_results):
    """
    Graph daily new cases, vaccinations, and death rates of age and ethnic groups in the US for all jurisdictions
    """

    # Filters for common trends and ethnicity/age-based trends in US data
    us_stats_ethn = [stat for stat in analysis.US_STATS if ("Death" in stat)]
    us_stats_ages = [stat for stat in analysis.US_STATS if ("year" in stat)]

    # Graph daily new cases per capita over time for every country (multiple countries / plot)
    visualization.plot_multi_line_graph(
        world_results.pivot_table(index="date", columns="location", values="new_cases"),
        "daily_new_cases_per_capita_over_time_for_all_countries",
        visualization.WORLD_EXT,
    )

    # Graph daily vaccinations per capita over time for every country (multiple countries / plot)
    visualization.plot_multi_line_graph(
        world_results.pivot_table(
            index="date", columns="location", values="daily_vaccinations"
        ),
        "daily_vaccinations_per_capita_over_time_for_all_countries",
        visualization.WORLD_EXT,
    )

    # Graph daily new cases per capita over time for every US state (multiple states / plot)
    visualization.plot_multi_line_graph(
        us_results.pivot_table(
            index="submission_date", columns="state", values="new_case"
        ),
        "daily_new_cases_per_capita_over_time_for_all_states",
        visualization.US_EXT,
    )

    # Graph daily vaccinations per capita over time for every US state (multiple states / plot)
    visualization.plot_multi_line_graph(
        us_results.pivot_table(
            index="submission_date", columns="state", values="daily_vaccinations"
        ),
        "daily_vaccinations_per_capita_over_time_for_all_states",
        visualization.US_EXT,
    )

    # Graph daily deaths of different ethnic groups per capita over time for every US state (multiple states / plot)
    for i in us_stats_ethn:
        visualization.plot_multi_line_graph(
            us_results.pivot_table(index="submission_date", columns="state", values=i),
            "daily_" + i + "_per_capita_over_time_for_all_states",
            visualization.US_EXT,
        )

    # Graph daily deaths of different age groups per capita over time for every US state (multiple states / plot)
    for i in us_stats_ages:
        visualization.plot_multi_line_graph(
            us_results.pivot_table(index="submission_date", columns="state", values=i),
            "daily_deaths_" + i + "_per_capita_over_time_for_all_states",
            visualization.US_EXT,
        )


def map_avg_trends(world_results_by_country, us_results_by_state, world_basemap, us_basemap):
    """
    Map average daily new cases, vaccinations, and death rates of age and
    ethnic groups in the US across time for all jurisdictions
    """

    # Filters for common trends and ethnicity/age-based trends in US data
    us_stats_ethn = [stat for stat in analysis.US_STATS if ("Death" in stat)]
    us_stats_ages = [stat for stat in analysis.US_STATS if ("year" in stat)]

    # Map average daily COVID-19 new cases per capita by country
    visualization.plot_map(
        world_results_by_country,
        "new_cases",
        "avg_daily_new_cases_per_capita_by_country",
        visualization.WORLD_EXT,
        "Reds",
        basemap=world_basemap,
    )

    # Map average daily COVID-19 vaccinations per capita by country
    visualization.plot_map(
        world_results_by_country,
        "daily_vaccinations",
        "avg_daily_vaccinations_per_capita_by_country",
        visualization.WORLD_EXT,
        "Blues",
        basemap=world_basemap,
        vmin=0.0,
        vmax=0.0005,
    )

    # Map average daily COVID-19 new cases per capita by state
    visualization.plot_map(
        us_results_by_state,
        "new_case",
        "avg_daily_new_cases_per_capita_by_state",
        visualization.US_EXT,
        "Reds",
        xlim=[-180, -50],
        basemap=us_basemap,
    )

    # Map average daily COVID-19 vaccinations per capita by state
    visualization.plot_map(
        us_results_by_state,
        "daily_vaccinations",
        "avg_daily_vaccinations_per_capita_by_state",
        visualization.US_EXT,
        "Blues",
        xlim=[-180, -50],
        basemap=us_basemap,
    )

    # Map average daily COVID-19 deaths of different ethnicities per capita by state
    for i in us_stats_ethn:
        visualization.plot_map(
            us_results_by_state,
            i,
            "avg_daily_" + i + "_per_capita_by_state",
            visualization.US_EXT,
            "Reds",
            xlim=[-180, -50],
            basemap=us_basemap,
        )

    # Map average daily COVID-19 deaths of different age groups per capita by state
    for i in us_stats_ages:
        visualization.plot_map(
            us_results_by_state,
            i,
            "avg_daily_deaths_" + i + "_per_capita_by_state",
            visualization.US_EXT,
            "Reds",
            xlim=[-180, -50],
            basemap=us_basemap,
        )


def plot_avg_trends(avg_world_results, avg_us_results):
    """
    Graph average daily new cases, vaccinations, and death rates of age and ethnic groups in the US across jurisdictions
    """

    # Filters for common trends and ethnicity/age-based trends in US data
    us_stats_common = [
        stat
        for stat in analysis.US_STATS
        if (("Death" not in stat) and ("year" not in stat))
    ]
    us_stats_ethn = [stat for stat in analysis.US_STATS if ("Death" in stat)]
    us_stats_ages = [stat for stat in analysis.US_STATS if ("year" in stat)]

    # Graph average new daily COVID-19 cases and vaccinations per capita for the world over time
    visualization.plot_line_graph(
        avg_world_results,
        analysis.WORLD_STATS,
        "avg_daily_new_cases_and_vaccinations_per_capita_over_time",
        visualization.WORLD_EXT,
    )

    # Graph average new daily COVID-19 cases and vaccinations per capita for the US over time
    visualization.plot_line_graph(
        avg_us_results,
        us_stats_common,
        "avg_daily_new_cases_and_vaccinations_per_capita_over_time",
        visualization.US_EXT,
    )

    # Select ethnic data
    avg_us_results_ethn = avg_us_results[us_stats_ethn]
    avg_us_results_ethn = avg_us_results_ethn[(avg_us_results_ethn.T != 0).any()]

    # Graph average daily COVID-19 deaths per capita for different ethnicities in the US over time
    visualization.plot_line_graph(
        avg_us_results_ethn,
        us_stats_ethn,
        "avg_daily_deaths_by_ethnicity_per_capita_over_time",
        visualization.US_EXT,
    )

    # Select age data
    avg_us_results_ages = avg_us_results[us_stats_ages]
    avg_us_results_ages = avg_us_results_ages[(avg_us_results_ages.T != 0).any()]

    # Graph average daily COVID-19 deaths per capita for different age groups in the US over time
    visualization.plot_line_graph(
        avg_us_results_ages,
        us_stats_ages,
        "avg_daily_deaths_by_age_per_capita_over_time",
        visualization.US_EXT,
    )


def main():
    """
    Download, process, and analyze COVID-19 data, before graphing all trends
    """

    # Download & retrieve COVID-19 data
    datasets = data_manager.get_dataset_info()
    data_manager.update_datasets(datasets)
    data = data_manager.retrieve_datasets(datasets)

    # Process & analyze world data
    world_c_data = data_processing.consolidate_world_data(data)
    world_pop = data_processing.get_world_pop_data(data)
    world_results = analysis.analyze_world_data(world_c_data, world_pop)

    # Process & analyze US data
    us_c_data = data_processing.consolidate_us_data(data)
    us_pop = data_processing.get_us_pop_data(data)
    us_results = analysis.analyze_us_data(us_c_data, us_pop)

    # Graph all trends (set DAILY_TRENDS_ENABLED = True for
    # detailed jurisdiction-by-jurisdiction data)

    if (DAILY_TRENDS_ENABLED):
        plot_daily_trends(world_results[0], us_results[0])

    map_avg_trends(
        world_results[1],
        us_results[1],
        data["world_countries_map"],
        data["us_states_map"],
    )
    plot_avg_trends(world_results[2], us_results[2])


if __name__ == "__main__":
    main()
