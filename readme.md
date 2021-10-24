# COVID-19 Vaccination Rollout Project

This is a data analysis project, written for my CSE 163 Intermediate Programming class at UW in Python with the help of the Pandas library. The goal of this project is to analyze the speed of the COVID-19 vaccine rollout across different jurisdictions, and see how it has impacted the virus's spread. There are many variables and players involved in this process, including the effectiveness and reach of distribution networks in different countries and states, as well as who is getting the vaccines and when. 

![Average Daily New Cases and Vaccinations Per Capita for the United States](/sample_visualizations/7_22_2021/plot_us_avg_daily_new_cases_and_vaccinations_per_capita_over_time.png)

Due to the life-threatening nature of inefficient distribution, stakeholders and the public have a right to clearly understand how quickly the COVID-19 vaccine rollout is progressing. By computing per capita case and vaccination rates across different countries and jurisdictions, and breaking these statistics down by age group and ethnicity in the United States, complex COVID-19 data can be visualized. This will reveal bottlenecks in the process, allowing the application of adequate resources to fixing them.

## Running the Code

*Note: this project has only been tested on Windows 10.*

To run the code, install `Python 3.9`, as well as the latest `pip` version for Python 3. Make sure both are in your environment `PATH`.

The following command will install all required packages: 

    pip install numpy pandas geopandas matplotlib requests zipfile shutil

<br>

A note about `geopandas` on Windows: `geopandas` requires  `fiona`, which depends on `gdal`. They can be found here:

https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal

https://www.lfd.uci.edu/~gohlke/pythonlibs/#fiona

Install them with:

`pip install path/to/gdal.whl`

`pip install path/to/fiona.whl`

<br>

When you have finished setting up the environment, run `main.py` to initiate the project. The datasets and visualizations will be output to the `datasets` and `visualizations` folders, respectively.

## Research Questions

In order to accomplish the goal described at the top of this document, I created four research questions:

1.	**What is the average number of Covid-19 vaccinations per capita per day by country?** Vaccination development, certification, and distribution infrastructure varies by country. I want to figure out which countries have the most effective processes for reaching herd immunity.

2.	**How does the average number of Covid-19 vaccinations per capita per day relate to the number of new Covid-19 cases by country?** I want to find how the speed of the vaccination rollout by country affects the spread of Covid-19, and whether it contributes to slowing down the virus.

3.	**What is the average number of Covid-19 vaccinations per capita per day by state, as well as age and ethnicity, in the United States?**  Specifically for the United States, I want to examine how well different states are implementing the Covid-19 vaccination rollout by age and ethnicity.

4.	**How does the average number of Covid-19 vaccinations per capita per day relate to the number of new Covid-19 cases by state, as well as age and ethnicity, in the United States?** I want to find how the speed of the vaccination rollout by state affects the spread of Covid-19, and whether it contributes to slowing down the virus for different age groups and ethnicities.

## Project Structure

This project was structured in such a way as to allow data to be piped from download, to processing, to analysis, and finally to visualization. The file structure is:

`main.py` - Main project file, runs the entire data pipeline

`data_manager.py` - Download and update all datasets

`data_processing.py` - Process and consolidate all datasets for analysis. This includes case, vaccination, death, geographic, and population data

`analysis.py` - Calculate per capita case, vaccination, and death data for a variety of jurisdictions, and across time

`visualization.py` - Plot line graphs, multiple line graphs, and maps of the analyzed data

`metadata` - A folder containing metadata on all project datasets, and references mapping jurisdiction names to various code formats

`sample_visualizations` - A folder containing some sample results of running this data analysis project

## Datasets

|Alias                    |URL                                                                                                                                                                    |
|-------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|world_covid_data         |https://github.com/owid/covid-19-data/blob/master/public/data/owid-covid-data.csv                                                                                      |
|us_covid_data            |https://data.cdc.gov/Case-Surveillance/United-States-COVID-19-Cases-and-Deaths-by-State-o/9mfq-cb36                                                                    |
|us_covid_age_deaths      |https://data.cdc.gov/NCHS/Provisional-COVID-19-Death-Counts-by-Sex-Age-and-S/9bhg-hcku/                                                                                |
|us_covid_ethnicity_deaths|https://docs.google.com/spreadsheets/d/e/2PACX-1vS8SzaERcKJOD_EzrtCDK1dX1zkoMochlA9iHoHg_RSw3V8bkpfk1mpw4pfL5RdtSOyx_oScsUtyXyk/pub?gid=43720681&single=true&output=csv|
|us_covid_vaccinations    |https://github.com/owid/covid-19-data/blob/master/public/data/vaccinations/us_state_vaccinations.csv                                                                   |
|world_covid_vaccinations |https://github.com/owid/covid-19-data/blob/master/public/data/vaccinations/vaccinations.csv                                                                            |
|world_locations          |https://github.com/owid/covid-19-data/blob/master/public/data/vaccinations/locations.csv                                                                               |
|world_countries_map      |https://hub.arcgis.com/datasets/2b93b06dc0dc4e809d3c8db5cb96ba69_0                                                                                                     |
|us_states_map            |https://www.weather.gov/gis/USStates                                                                                                                                   |
|world_population         |https://population.un.org/wpp/Download/Standard/CSV/                                                                                                                   |
|us_population            |https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/national/totals/                                                                                    |

*Note: The raw dataset URLs can be found in `metadata\datasets.csv`*
