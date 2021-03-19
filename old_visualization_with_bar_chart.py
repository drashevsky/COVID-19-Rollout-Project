"""
Daniel Rashevsky
CSE 163 AE
This file visualizes and graphs the data analyzed in data_analysis
"""

import pandas as pd
import geopandas as gpd
import numpy as np

from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
import matplotlib.font_manager as fnt
import matplotlib.dates as date_format

import sys
import os

import data_manager
import data_processing
import analysis

VIZ_PATH = "visualizations"
MAP_EXT = "map"
PLOT_EXT = "plot"
WORLD_EXT = "world"
US_EXT = "us"


def plot_map(data, column, name, extension, xlim=None, basemap=None):
    """
    Given a dataframe, basemap geodataframe, column to graph, name, data category extension,
    and x-axis range plots a map with data attributes from the column
    """

    print("Graphing " + name + " for " + extension + "...")

    # Create graph directory if needed
    if not os.path.isdir(VIZ_PATH):
        os.mkdir(VIZ_PATH)

    # Convert data to geodataframe
    data = gpd.GeoDataFrame(data)

    # Setup map
    (fig, ax) = plt.subplots(figsize=(18, 9))
    ax.set_title(name)
    cax = make_axes_locatable(ax).append_axes("right", size="5%", pad=0.1)

    # Limit map x-axis to certain range
    if xlim is not None:
        ax.set_xlim(xlim)

    # Plot basemap
    if basemap is not None:
        basemap.plot(ax=ax, color="#CCCCCC", cax=cax)

    # Plot column
    data.plot(column=column, legend=True, ax=ax, cax=cax, cmap="Reds")

    # Save map
    fig.canvas.start_event_loop(sys.float_info.min)
    fig.savefig(
        VIZ_PATH + "/" + MAP_EXT + "_" + extension + "_" + name + ".png",
        bbox_inches="tight",
    )


def plot_graph(data, columns, name, extension, bar = False):
    """
    Given a dataframe, column to graph, name, data category extension,
    and chart type plots a chart with data attributes from the column
    """

    print("Graphing " + name + " for " + extension + "...")

    # Create graph directory if needed
    if not os.path.isdir(VIZ_PATH):
        os.mkdir(VIZ_PATH)

    # Setup graph
    (fig, ax) = plt.subplots()
    ax.set_title(name)

    # Setup legend
    fontP = fnt.FontProperties()
    fontP.set_size("xx-small")

    # Plot columns
    data = data[columns]
    if bar:
        data.plot.bar(legend=True, ax=ax)
        ax.xaxis.set_major_locator(date_format.YearLocator())
        ax.xaxis.set_major_formatter(date_format.DateFormatter('%Y'))
        ax.xaxis_date()
        fig.autofmt_xdate()
    else:
        data.plot(legend=True, ax=ax)

    # Plot legend
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", prop=fontP)

    # Save plot
    fig.savefig(
        VIZ_PATH + "/" + PLOT_EXT + "_" + extension + "_" + name + ".png",
        bbox_inches="tight",
    )


def main():
    """
    Tests all functionality and creates a graph tracking new cases and vaccinations over time for the US and world
    """

    # Test dataset_mgr
    datasets = data_manager.get_dataset_info()
    data_manager.update_datasets(datasets)
    data = data_manager.retrieve_datasets(datasets)

    # Test dataset_processing for world data
    world_c_data = data_processing.consolidate_world_data(data)
    world_pop = data_processing.get_world_pop_data(data)
    world_results = analysis.analyze_world_data(world_c_data, world_pop)

    # Test dataset_processing for US data
    us_c_data = data_processing.consolidate_us_data(data)
    us_pop = data_processing.get_us_pop_data(data)
    us_results = analysis.analyze_us_data(us_c_data, us_pop)

    # Test visualization: graph average daily cases and vaccinations per capita for the world
    plot_graph(
        world_results[2],
        ["new_cases", "daily_vaccinations"],
        "avg_cases_and_vaccinations_over_time",
        WORLD_EXT,
    )

    # Test visualization: graph average daily cases and vaccinations per capita in the US
    plot_graph(
        us_results[2],
        ["new_case", "daily_vaccinations"],
        "avg_cases_and_vaccinations_over_time",
        US_EXT,
    )

    # Test visualization: graph average daily American Indian and Alaska Native COVID deaths per capita in the US
    plot_graph(
        us_results[2],
        ["Deaths_AIAN"],
        "avg_AIAN_deaths_per_capita_over_time",
        US_EXT,
        bar = True
    )

    # Test visualization: map average American Indian and Alaska Native COVID deaths per capita by state in the US
    plot_map(
        us_results[1],
        "Deaths_AIAN",
        "avg_AIAN_deaths_per_capita_by_US_state",
        US_EXT,
        xlim=[-180, -50],
        basemap=data["us_states_map"],
    )

    # Test visualization: map average new cases per capita by country
    plot_map(
        world_results[1],
        "new_cases",
        "avg_new_cases_per_capita_by_country",
        WORLD_EXT,
        basemap=data["world_countries_map"],
    )


if __name__ == "__main__":
    main()
