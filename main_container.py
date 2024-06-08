# Main container setup
import numpy as np
from scipy import stats
import streamlit as st
import plotly.express as px
import pandas as pd
from plotly.colors import n_colors

def get_driver_ids(drivers, drivers_df):
    driver_ids = []
    for driver in drivers:
        driver_name = driver.split(" ")
        driver_id = drivers_df.loc[(drivers_df["forename"] == driver_name[0]) & (drivers_df["surname"] == driver_name[1]), "driver_id"]

        items = driver_id.items() # Series size should always be 1 because 'ID' is unique
        for item in items:
            driver_ids.append(item[1])

    return driver_ids


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
    
    best_time = 999999
    time = 0
    c_name = ""
    for obj in fastest_laps_per_race.values():
        mscds = obj["ms"]
      
        if mscds < best_time: 
            best_time = mscds
            time = obj["time"]

            b = list(fastest_laps_per_race.keys())[list(fastest_laps_per_race.values()).index(obj)]
           
            # c_name = c_df.loc[c_df['circuit_id'] == b, "name"]

    if time == 0 : time="No time set"
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Wins", value=int(driver_wins))
    col2.metric("Fastest Lap", value=f"{time} CIRCUIT")
    col3.metric("Total Points", value= int(driver_points))


def final_pos_graph(year, results_df, races_df, d_ids):
    if (len(d_ids) == 1):
        for d_id in d_ids:
            names = []
            finals = {"x": [], "y": []}
            pos_order = []

            races_df = races_df.loc[races_df["year"] == year, ["race_id", "circuit_id", "name"]]
            for index, r in races_df.iterrows():
                # Obtains each race the selected driver was in for the selected year
                race_pos = results_df.loc[(results_df["race_id"] == r["race_id"]) & (results_df["driver_id"] == d_id), "position"]
                race_pos = race_pos.replace('\\N','DNF')

                names.append(r["name"])
                for pos in race_pos.items():
                    finals["x"].append(r["race_id"])
                    finals["y"].append(pos[1])
                    if pos[1] != "DNF":
                        pos_order.append(int(pos[1]))

            df = pd.DataFrame(data=finals)
            pos_order.sort() # Orders positions by numbers
            
            pos_order.append("DNF") # Adds DNF position for bottom of graph

            fig = px.line(df, x="x", y="y", title=f"Finishing Positions",
                        labels = {"x": "Race", "y": "Final position"}, markers=True)
                            
            fig.update_layout(
                xaxis = dict(
                    tickangle = -45,
                    tickmode = 'array',
                    tickvals = df["x"],
                    ticktext = names,
                    type = "category"),
                yaxis = dict(
                    type = "category",
                    categoryorder ='array', 
                    autorange = "reversed",
                    categoryarray = pos_order)
            )

            fig.update_traces(line_color="#FF4B4B")
            st.plotly_chart(fig, use_container_width=True)


def lap_times_graph(year, d_ids, laps_df, races_df, col):
    for d_id in d_ids:
        times = {"x": [], "y": [], "Name": [], "Lap": [], "Time": []}

        # Obtains each race the selected driver was in for the selected year
        races_df = races_df.loc[races_df["year"] == year, ["race_id", "name"]]
        for index, r in races_df.iterrows():
            df_laps = laps_df.loc[(laps_df["race_id"] == r["race_id"]) & (laps_df["driver_id"] == d_id), ["lap", "time", "milliseconds"]]
            df_laps2 = df_laps.sort_values(by="milliseconds")

            for index, r1 in df_laps.iterrows():
                times["x"].append(r1["milliseconds"])
                times["y"].append(r["race_id"])
                times["Name"].append(r["name"])
                times["Lap"].append(r1["lap"])
                times["Time"].append(r1["time"])
               
        df = pd.DataFrame(data=times)

        # Remove outliers
        z = np.abs(stats.zscore(df['x']))
        threshold = 3
        outliers = df[z > threshold]
        df = df.drop(outliers.index)
        print(df)
        fig = px.strip(df, x="x", y="y",title="Lap Times<br><sub class='subtitle'>Hover over points for more details</sub>",
                       labels = {"x": "Lap time", "y": "Race"}, 
                       color_discrete_sequence = n_colors("rgb(255, 75, 75)", "rgb(255,255,255)", 3, colortype="rgb"), color="y", 
                       hover_name="Name", hover_data={"x":False, "y":False, "Lap":True, "Time":True})
        
        fig.update_xaxes(type='date', tickformat='%M:%S.%f%f')
        fig.update_layout(
            showlegend = False,
            yaxis = dict(
                side = "right",
                showticklabels = False),
            xaxis = dict(
                tickangle = -45)
        )
        col.plotly_chart(fig, use_container_width=True)


def points_graph(year, d_ids, col, races_df, results_df):
    points = {"x":[], "y":[], "Name":[]}
    for d_id in d_ids:
        # Obtains each race the selected driver was in for the selected year
        races_df = races_df.loc[races_df["year"] == year, ["race_id", "name"]]
        for index, r in races_df.iterrows():
            df_points = results_df.loc[(results_df["race_id"] == r["race_id"]) & (results_df["driver_id"] == d_id), "points"]
            for race in df_points.items():
                points["y"].append(race[1])
                points["x"].append(r["race_id"])
                name = r["name"].replace("Grand Prix", "GP")
                points["Name"].append(name)

    df = pd.DataFrame(data=points)
    fig = px.bar(df, x="x", y="y",
                 title="Race Points",
                 labels = {"x": "Race", "y": "Points"},
                 hover_name="Name", hover_data={"x":False, "y":True, "Name":False})
    
    fig.update_traces(marker_color = '#FF4B4B')
    fig.update_layout(
            showlegend = False,
            yaxis = dict(
                side = "right"),
            xaxis = dict(
                tickangle = -45,
                tickmode = 'array',
                tickvals = df["x"],
                ticktext = df["Name"],
                type = "category")
    )
    col.plotly_chart(fig, use_container_width=True)


def Main_Setup(filter_data, dfs):
    # Dataframes
    standings_df = dfs["driver_standings"]
    races_df = dfs["races"]
    drivers_df = dfs["drivers"]
    laps_df = dfs["laps"]
    c_df = dfs["circuits"]
    results_df = dfs["results"]

    year = filter_data["year"]
    drivers = filter_data["drivers"]

    st.header(f"Performance Overview - {year}", anchor=False)

    if (len(drivers) == 0):
        st.text("Select driver(s) to view performance overview")

    driver_ids = get_driver_ids(drivers, drivers_df)
    final_pos_graph(year, results_df, races_df, driver_ids)
        
    if (len(drivers) == 1):
        #TODO OLDER RACES AND DRIVER DATA NOT ALWAYS REGISTERING - MOSTLY LAPTIMES and D_ID
        #TODO MAKE GET RACES PER YEAR FOR EACH DRIVER MODULAR
        #TODO MULTI DRIVER SELECTIONS
        #TODO LAP TIMES LABELS AND REMOVE 'GRAND PRIX' ON POINTS CHART LABELS
        #TODO FASTEST LAP - CIRCUIT PRINT
        

        metric_setup(year, drivers, standings_df, races_df, drivers_df, laps_df, c_df)

        col1, col2 = st.columns(2, gap="large")
        lap_times_graph(year, driver_ids, laps_df, races_df, col1)
        points_graph(year, driver_ids, col2, races_df, results_df)