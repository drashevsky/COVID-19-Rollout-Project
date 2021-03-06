"""
Daniel Rashevsky
CSE 163 AE
This file provides functions for visualizing and graphing the data analyzed in data_analysis
"""

import pandas as pd
import geopandas as gpd
import numpy as np

from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
import matplotlib.font_manager as fnt

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
NUM_MULTI_PLOTS = 7


def plot_map(data, column, name, extension, cmap, xlim=None, basemap=None, vmin=None, vmax=None):
    """
    Given a dataframe, column to graph, name, data category extension, colormap,
    optional x-axis range, optional basemap geodataframe, and optional vmin/vmax
    normalization parameters, plots a map with data attributes from the column
    """

    print("Graphing " + name + " for " + extension + "...")

    # Create graph directory if needed
    if not os.path.isdir(VIZ_PATH):
        os.mkdir(VIZ_PATH)

    # Convert data to geodataframe
    data = gpd.GeoDataFrame(data)

    # Setup map
    (fig, ax) = plt.subplots(figsize=(18, 9), dpi=200)
    ax.set_title(name)
    cax = make_axes_locatable(ax).append_axes("right", size="5%", pad=0.1)

    # Limit map x-axis to certain range
    if xlim is not None:
        ax.set_xlim(xlim)

    # Set normalization
    if (vmin is not None and vmax is not None):
        norm = plt.Normalize(vmin=vmin, vmax=vmax)
    else:
        norm = None

    # Plot basemap
    if basemap is not None:
        basemap.plot(ax=ax, color="#CCCCCC", cax=cax)

    # Plot column
    data.plot(column=column, legend=True, ax=ax, cax=cax, cmap=cmap, norm=norm)

    # Save map
    fig.canvas.start_event_loop(sys.float_info.min)
    fig.savefig(
        VIZ_PATH + "/" + MAP_EXT + "_" + extension + "_" + name + ".png",
        bbox_inches="tight",
    )

    # Close figure
    plt.close(fig)


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
    (fig, ax) = plt.subplots(dpi=200)
    ax.set_title(name)

    # Setup legend
    fontP = fnt.FontProperties()
    fontP.set_size("xx-small")

    # Plot columns
    data = data[columns]
    data.plot(legend=True, ax=ax)
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", prop=fontP)
    fig.autofmt_xdate()

    # Save columns
    fig.savefig(
        VIZ_PATH + "/" + PLOT_EXT + "_" + extension + "_" + name + ".png",
        bbox_inches="tight",
    )

    # Close figure
    plt.close(fig)


def plot_multi_line_graph(data, title, extension):
    """
    Given a dataframe containing a single statistic to map and multiple columns
    representing different jurisdictions, a common graph title, and a data category
    extension, create a series of plots containing the graphs of that statistic
    across those jurisdictions
    """

    # Divide dataframe into several plots
    cols = list(data.columns)
    total_cols = len(cols)
    vars_per_plot = total_cols // NUM_MULTI_PLOTS

    # Graph, name, and save each plot
    for i in range(0, total_cols, vars_per_plot):
        plot_line_graph(
            data,
            cols[i : i + vars_per_plot],
            title + "_" + str(i // vars_per_plot),
            extension
        )


def main():
    """
    Tests all functionality and creates graphs tracking new cases and vaccinations over time for the US and world,
    as well as maps tracking death rates and new cases
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
    plot_line_graph(
        world_results[2],
        ["new_cases", "daily_vaccinations"],
        "avg_cases_and_vaccinations_over_time",
        WORLD_EXT,
    )

    # Test visualization: graph average daily cases and vaccinations per capita in the US
    plot_line_graph(
        us_results[2],
        ["new_case", "daily_vaccinations"],
        "avg_cases_and_vaccinations_over_time",
        US_EXT,
    )

    # Test visualization: map average American Indian and Alaska Native COVID deaths per capita by state in the US
    plot_map(
        us_results[1],
        "Deaths_AIAN",
        "avg_AIAN_deaths_per_capita_by_US_state",
        US_EXT,
        "Reds",
        xlim=[-180, -50],
        basemap=data["us_states_map"],
    )

    # Test visualization: map average new cases per capita by country
    plot_map(
        world_results[1],
        "new_cases",
        "avg_new_cases_per_capita_by_country",
        WORLD_EXT,
        "Reds",
        basemap=data["world_countries_map"],
    )


if __name__ == "__main__":
    main()
