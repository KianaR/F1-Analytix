import sys
import streamlit as st
import pandas as pd
import os
import warnings

warnings.filterwarnings("ignore")

from sidebar import SB_Setup
from main_container import Main_Setup

# Page Setup
st.set_page_config(page_title="F1 ATX 0.0.1", page_icon=":checkered_flag:", layout="wide")
st.title(":checkered_flag: F1 Analytix", anchor=False)

filename = "main.css"
try:
    with open(filename) as file:
        css = file.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
except OSError:
    print ("Could not read file:", filename)

st.sidebar.header("F1 ATX")
st.sidebar.subheader("Settings")

# Dataframe setup
driver_df = pd.read_csv("./f1_data/drivers.csv")
ds_df = pd.read_csv("./f1_data/driver_standings.csv")
race_df = pd.read_csv("./f1_data/races.csv")
laps_df = pd.read_csv("./f1_data/lap_times.csv")
c_df = pd.read_csv("./f1_data/circuits.csv")

race_df.rename(columns={"raceId": "race_id", "circuitId": "circuit_id"}, inplace = True)
driver_df.rename(columns={"driverId": "driver_id", "driverRef": "driver_ref"}, inplace = True)
ds_df.rename(columns={"driverStandingsId": "driver_standings_id", "raceId": "race_id", "driverId": "driver_id", "positionText": "postiion_text"}, inplace = True)
laps_df.rename(columns={"raceId": "race_id", "driverId": "driver_id"}, inplace = True)
c_df.rename(columns={"circuitId": "circuit_id", "circuitRef": "circuit_ref"}, inplace = True)

# Side Bar setup
dfs = {"drivers": driver_df, "driver_standings": ds_df, "races": race_df, "laps": laps_df, "circuits": c_df}
filters = SB_Setup(dfs)

# Main Container setup
Main_Setup(filters, dfs)


