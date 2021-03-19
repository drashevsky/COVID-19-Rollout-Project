"""
Daniel Rashevsky
CSE 163 AE
This file downloads and manages updates for all datasets in datasets.csv
"""

import pandas as pd
import geopandas as gpd
import numpy as np

import requests
import zipfile
import datetime
import shutil
import os

DATASET_INFO = "metadata/datasets.csv"
UPDATE_INFO = "timestamps.csv"
DATASET_DIR = "datasets"
DAYS_BETWEEN_UPDATE = 2
STREAM_CHUNK_SZ = 8192


def download_file(metadata_row):
    """
    Download a single dataset given by its information, unzip if it is in zip folder
    """

    # Get needed file metadata
    is_zip = metadata_row["Is_Zip"]
    extract_filename = metadata_row["Extract_FileName"]

    # Generate filenames
    fname = metadata_row["Alias"]
    download_fname = fname + (".csv" if not is_zip else ".zip")
    save_fname = fname + (
        ".csv" if not is_zip else os.path.splitext(extract_filename)[1]
    )
    print("Downloading " + fname + "...")

    # Download file
    with requests.get(metadata_row["URL"], stream=True) as r:
        r.raise_for_status()
        with open(DATASET_DIR + "/" + download_fname, "wb") as f:
            for chunk in r.iter_content(chunk_size=STREAM_CHUNK_SZ):
                f.write(chunk)

    # If the file is compressed, extract it
    if is_zip:
        print("Unzipping " + fname + "...")

        z = zipfile.ZipFile(DATASET_DIR + "/" + download_fname)
        for f in z.infolist():
            f.filename = fname + os.path.splitext(f.filename)[1]
            z.extract(f, path=DATASET_DIR)

        z.close()
        os.remove(DATASET_DIR + "/" + download_fname)


def download_files(metadata_frame, timestamps):
    """
    Download multiple datasets, given a set of datasets to download and their last update times
    """

    # Download every dataset in dataframe
    for i, row in metadata_frame.iterrows():
        try:
            alias = metadata_frame.loc[i, "Alias"]
            download_file(metadata_frame.loc[i])
            timestamps.loc[alias, "TimeStamp"] = datetime.datetime.now()
        except Exception as e:
            print("File failed to download. Error: " + str(e))


def check_aliases_exist(metadata_frame):
    """
    Given a set of datasets to check, checks if datasets specified by datasets.csv are already downloaded
    """

    exists = []

    for i, row in metadata_frame.iterrows():

        # Get filename
        alias = metadata_frame.loc[i, "Alias"]
        is_zip = metadata_frame.loc[i, "Is_Zip"]
        extract_filename = metadata_frame.loc[i, "Extract_FileName"]
        fname = alias + (
            ".csv" if not is_zip else os.path.splitext(extract_filename)[1]
        )

        # Check if file exists
        exists.append(not os.path.exists(DATASET_DIR + "/" + fname))

    return pd.Series(exists)


def get_dataset_info():
    """
    Get metadata on all datasets
    """

    return pd.read_csv(DATASET_INFO)


def update_datasets(metadata_frame):
    """
    Given a set of datasets, update them
    """

    dir_exists = os.path.isdir(DATASET_DIR)

    # Create new dataset age tracking frame
    timestamps = pd.DataFrame()

    if dir_exists:

        # Find stale datasets
        if os.path.exists(UPDATE_INFO):
            timestamps = pd.read_csv(
                UPDATE_INFO, parse_dates=["TimeStamp"], index_col=0
            )
            timestamp_deltas = (
                datetime.datetime.now() - timestamps["TimeStamp"]
            ).dt.days
            timestamp_deltas.index = range(len(timestamp_deltas))
            stale_mask = timestamp_deltas >= metadata_frame["Update_Interval"]
        else:
            stale_mask = True

        # Find missing datasets
        exists_mask = check_aliases_exist(metadata_frame)

        # Update them
        download_files(metadata_frame[stale_mask | exists_mask], timestamps)

    else:

        # Create directory to hold datasets
        os.mkdir(DATASET_DIR)

        # Download all datasets
        download_files(metadata_frame, timestamps)

    # Update dataset info
    timestamps.to_csv(UPDATE_INFO)


def retrieve_datasets(metadata_frame):
    """
    Given a set of datasets, search folder and return them as dataframes
    """

    data_dict = {}

    for i, row in metadata_frame.iterrows():

        # Get file metadata
        alias = metadata_frame.loc[i, "Alias"]
        is_zip = metadata_frame.loc[i, "Is_Zip"]
        is_shapefile = metadata_frame.loc[i, "Is_ShapeFile"]
        extract_filename = metadata_frame.loc[i, "Extract_FileName"]

        # Get filename
        fname = alias + (
            ".csv" if not is_zip else os.path.splitext(extract_filename)[1]
        )

        # Check if file exists
        if os.path.exists(DATASET_DIR + "/" + fname):
            if is_shapefile:
                data_dict[alias] = gpd.read_file(DATASET_DIR + "/" + fname)
            else:
                data_dict[alias] = pd.read_csv(DATASET_DIR + "/" + fname)

    return data_dict


def main():
    """
    Test all methods in data manager
    """

    # Test retrieve
    datasets = get_dataset_info()
    update_datasets(datasets)

    # Test no changes
    update_datasets(datasets)

    # Test remove all
    shutil.rmtree(DATASET_DIR)
    update_datasets(datasets)

    # Test remove multiple random
    os.remove(DATASET_DIR + "/us_states_map.shp")
    os.remove(DATASET_DIR + "/world_covid_vaccinations.csv")
    os.remove(DATASET_DIR + "/us_covid_data.csv")
    update_datasets(datasets)

    # Print results
    print(retrieve_datasets(datasets).keys())
    print(datasets)


if __name__ == "__main__":
    main()
