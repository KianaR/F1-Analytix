# Sidebar setup
import pandas as pd
import streamlit as st


def clear_drivers():
    st.session_state.driver_input = []

def year_picker(df):
    min_yr = (df["year"]).min()
    max_yr = (df["year"]).max()
    year_input = st.sidebar.slider("Year", min_yr, max_yr-1, on_change=clear_drivers, key="year_input")
    return year_input

def driver_select(drivers_df, races_df, standings_df, yr):
    # Obtains each race that was in the selected year
    driver_names = []

    races_df = races_df.loc[races_df["year"] == yr, "race_id"]
    for race in races_df.items():
        # Obtains each driver for each race in that year
        drivers = standings_df.loc[standings_df["race_id"] == race[1], "driver_id"]
        for d in drivers.items():
            # Obtains each driver's name for each driver in each race for that year
            driver = drivers_df.loc[drivers_df["driver_id"] == d[1],  ['forename', 'surname']]
            for index, row in driver.iterrows():
                name = f"{row['forename']} {row['surname']}"
                if (name not in driver_names):
                    driver_names.append(name)

    driver_input = st.sidebar.multiselect("Driver(s)", options=driver_names, key="driver_input")
    return driver_input

def SB_Setup(dfs):
    yr_s = year_picker(dfs["races"])
    driver_s = driver_select(dfs["drivers"], dfs["races"], dfs["driver_standings"], yr_s) 
    
    return ({
        "year": yr_s,
        "drivers": driver_s
    })