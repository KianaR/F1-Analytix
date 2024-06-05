# Main container setup
import streamlit as st
import plotly.express as px
import pandas as pd

def metric_setup(year, driver, standings_df, races_df, drivers_df, laps_df, c_df):
    driver_name = driver[0].split(" ")
    driver_id = drivers_df.loc[(drivers_df["forename"] == driver_name[0]) & (drivers_df["surname"] == driver_name[1]), "driver_id"]
    
    driver_points = 0
    driver_wins = 0

    for d in driver_id.items():
        d_id = d[1]

    fastest_laps_per_race = {}

    races_df = races_df.loc[races_df["year"] == year, ["race_id", "circuit_id"]]
    for index, r in races_df.iterrows():
        # Obtains each race the selected driver was in for the selected year
        dvrs = standings_df.loc[(standings_df["race_id"] == r["race_id"]) & (standings_df["driver_id"] == d_id), ["points", "wins"]]
        driver_points = dvrs["points"].max()
        driver_wins = dvrs["wins"].max()

        # Obtains all lap times for that race
        lap_times = laps_df.loc[(laps_df["race_id"] == r["race_id"]) & (laps_df["driver_id"] == d_id), ["time", "milliseconds"]]
        fastest = 999999 # Milliseconds stores the time in milliseconds
        time = 0
        for index, row in lap_times.iterrows():
            if row["milliseconds"] < fastest:
                fastest = row["milliseconds"]
                time = row["time"]

                if time != 0:
                    fastest_laps_per_race[r["circuit_id"]] = {"time": row["time"], "ms": row["milliseconds"], "race":r["race_id"]}
    
    # best_time = 999999
    # time = 0
    # c_name = ""
    # for obj in fastest_laps_per_race.values():
    #     mscds = obj["ms"]
      
    #     if mscds < best_time: 
    #         best_time = mscds
    #         time = obj["time"]

    #         b = list(fastest_laps_per_race.keys())[list(fastest_laps_per_race.values()).index(obj)]
           
            #print("circ: ", b)
           # circuit = c_df.loc[c_df['circuit_id'] == b]
           
           # print("name: ", circuit["name"], "ms2: ", best_time, "race: ", obj["race"])
           # c_name = circuit["name"]

    #if time == 0 : time="No time set"
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Wins", value=int(driver_wins))
    col2.metric("Fastest Lap", value="xxx")
    col3.metric("Total Points", value= int(driver_points))


def Main_Setup(filter_data, dfs):
    # Dataframes
    standings_df = dfs["driver_standings"]
    races_df = dfs["races"]
    drivers_df = dfs["drivers"]
    laps_df = dfs["laps"]
    c_df = dfs["circuits"]

    st.header("Stats Overview", anchor=False)

    year = filter_data["year"]
    drivers = filter_data["drivers"]

    if (len(drivers) == 1):
        #TODO OLDER RACES AND DRIVERS MISSING DATA
        metric_setup(year, drivers, standings_df, races_df, drivers_df, laps_df, c_df)
