"""
Daniel Rashevsky
CSE 163 AE
This file visualizes and graphs the data analyzed in data_analysis
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fnt
import os

import data_manager
import data_processing
import analysis

VIZ_PATH = "visualizations"
MAP_EXT = "map"
PLOT_EXT = "plot"
WORLD_EXT = "world"
US_EXT = "us"


def plot_map(data, column, name, extension):
    """
    Given a geodataframe, column to graph, name, and data category extension
    plots a map with data attributes from the column
    """

    print("Graphing " + name + " for " + extension + "...")

    # Create graph directory if needed
    if not os.path.isdir(VIZ_PATH):
        os.mkdir(VIZ_PATH)

    # Setup map
    (fig, ax) = plt.subplots()
    ax.set_title(name)
    data.plot(ax=ax, color="#CCCCCC")

    # Plot and save column
    data.plot(column=column, legend=True, ax=ax)
    fig.savefig(
        VIZ_PATH + "/" + MAP_EXT + "_" + extension + "_" + name + ".png",
        bbox_inches="tight",
    )


def plot_line_graph(data, columns, name, extension):
    """
    Given a dataframe, column to graph, name, and data category extension
    plots a map with data attributes from the column
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

    # Plot and save column
    data = data[columns]
    data.plot(legend=True, ax=ax)
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", prop=fontP)
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

    # Test visualization: graph daily cases and vaccinations per capita for the world
    plot_line_graph(
        world_results[2],
        ["new_cases", "daily_vaccinations"],
        "cases_and_vaccinations_over_time",
        WORLD_EXT,
    )

    # Test visualization: graph daily cases and vaccinations per capita in the US
    plot_line_graph(
        us_results[2],
        ["new_case", "daily_vaccinations"],
        "cases_and_vaccinations_over_time",
        US_EXT,
    )


if __name__ == "__main__":
    main()
