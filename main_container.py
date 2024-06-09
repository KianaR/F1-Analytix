# Main container setup
import numpy as np
from scipy import stats
import streamlit as st
import plotly.express as px
import pandas as pd
from plotly.colors import n_colors
from plotly import graph_objects as go


def get_driver_names_from_id(drivers, drivers_df):
    driver_names = []
    for driver in drivers:
        driver_names_df = drivers_df.loc[(drivers_df["driver_id"] == driver), ["forename", "surname"]]
        for i, row in driver_names_df.iterrows():
            name = row["forename"] + " " + row["surname"]
            driver_names.append(name)
    return driver_names
         
def get_driver_ids(drivers, drivers_df):
    driver_ids = []
    for driver in drivers:
        driver_name = driver.split(" ")
        driver_id = drivers_df.loc[(drivers_df["forename"] == driver_name[0]) & (drivers_df["surname"] == driver_name[1]), "driver_id"]

        items = driver_id.items() # Series size should always be 1 because 'ID' is unique
        for item in items:
            driver_ids.append(item[1])

    return driver_ids


def metric_setup(year, d_ids, standings_df, races_df, drivers_df, laps_df, c_df):
    data = {}
    count = len(d_ids)

    for d_name in d_ids:
        data[d_name] = {"points": 0, "wins": 0 }

        driver_name = d_name.split(" ")
        driver_id = drivers_df.loc[(drivers_df["forename"] == driver_name[0]) & (drivers_df["surname"] == driver_name[1]), "driver_id"]

        for d in driver_id.items():
            d_id = d[1]

        fastest_laps_per_race = {}

        races = races_df.loc[races_df["year"] == year, ["race_id", "circuit_id"]]
        for index, r in races.iterrows():
            # Obtains each race the selected driver was in for the selected year
            dvrs = standings_df.loc[(standings_df["race_id"] == r["race_id"]) & (standings_df["driver_id"] == d_id), ["points", "wins"]]
            data[d_name]["points"] = dvrs["points"].max()
            data[d_name]["wins"] = dvrs["wins"].max()

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

            data[d_name]["fastest_laps"] = fastest_laps_per_race
    
    best_time = [999999, ""]
    time = 0
    wins = [0, ""]
    points = [0, ""]
    for driver in data:
        if data[driver]["wins"] > wins[0]:
            wins[0] = data[driver]["wins"]
            wins[1] = driver
        if data[driver]["points"] > points[0]:
            points[0] = data[driver]["points"]
            points[1] = driver

        for obj in data[driver]["fastest_laps"].values():
            mscds = obj["ms"]
            if mscds < best_time[0]: 
                best_time[0] = mscds
                time = obj["time"]
                best_time[1] = driver

                # b = list(fastest_laps_per_race.keys())[list(fastest_laps_per_race.values()).index(obj)]
                # c_name = c_df.loc[c_df['circuit_id'] == b, "name"]

    if wins[1] == "":
        wins.pop(1)
    if points[1] == "":
        points.pop(1)
    if best_time[1] == "":
        best_time.pop(1)
    
    val_wins = wins[0] 
    title_wins = "Total Wins"
    val_points = int(points[0])
    title_points = "Total Points"
    title_time = "Fastest Lap"
    if time == 0: time="No time set"
    val_time = time

    if count > 1:
        title_wins = "Most Wins"
        title_points = "Most Points"
        if len(wins)==2:
            val_wins = f"{wins[1]} [{wins[0]}]"
        else:
            val_wins = "N/A"

        if len(points)==2:
            val_points = f"{points[1]} [{int(points[0])}]"
        else:
            val_points = "N/A"

        if len(best_time)==2:
            val_time = f"{best_time[1]} [{time}]"

    col1, col2, col3 = st.columns(3)
    col1.metric(title_wins, value=val_wins)
    col2.metric(title_time, value=val_time)
    col3.metric(title_points, value=val_points)


def final_pos_graph(year, results_df, races_df, d_ids, drivers_df, scale):
    finals = {}
    count = len(d_ids)
    for i in range(len(d_ids)):
        finals[f"x{i}"] = []
        finals[f"y{i}"] = []

    names = []
    pos_order = []
    drivers = get_driver_names_from_id(d_ids, drivers_df)

    for i, d_id in enumerate(d_ids):
        races  = races_df.loc[races_df["year"] == year, ["race_id", "circuit_id", "name"]]
        for index, r in races.iterrows():
            # Obtains each race the selected driver was in for the selected year
            race_pos = results_df.loc[(results_df["race_id"] == r["race_id"]) & (results_df["driver_id"] == d_id), "position"]
            race_pos = race_pos.replace('\\N','DNF')

            if r["name"] not in names: names.append(r["name"])
            for pos in race_pos.items():
                finals[f"x{i}"].append(r["race_id"])
                finals[f"y{i}"].append(pos[1])

                if pos[1] not in pos_order:
                    if pos[1] != "DNF":
                        pos_order.append(int(pos[1]))

    fig = go.Figure()
    vals = []
    
    for num in range(count):
        for v in finals[f"x{num}"]:
            vals.append(v)
        fig.add_trace(go.Scatter(x=finals[f"x{num}"], y=finals[f"y{num}"], name=drivers[num], mode="markers+lines", line_color=scale[num]))
        
    pos_order.sort() # Orders positions by numbers
    pos_order.append("DNF") # Adds DNF position for bottom of graph

    fig.update_layout(
        title=go.layout.Title(text="Finishing Positions"),
        xaxis = dict(
            title = "Race",
            tickangle = -45,
            tickmode = 'array',
            tickvals = vals,
            ticktext = names,
            type = "category"),
        yaxis = dict(
            title = "Finishing Position",
            type = "category",
            categoryorder ='array', 
            autorange = "reversed",
            categoryarray = pos_order)
    )

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


def points_graph(year, d_ids, col, races_df, results_df, scale, drivers_df):
    d_names = get_driver_names_from_id(d_ids, drivers_df)
    race_names = []

    final_points = {}
    count = len(d_ids)
    for i in range(len(d_ids)):
        final_points[f"x{i}"] = []
        final_points[f"y{i}"] = []

    for i, d_id in enumerate(d_ids):
        # Obtains each race the selected driver was in for the selected year
        races = races_df.loc[races_df["year"] == year, ["race_id", "name"]]
        for index, r in races.iterrows():

            name = r["name"].replace("Grand Prix", "GP")
            if name not in race_names: race_names.append(name)

            df_points = results_df.loc[(results_df["race_id"] == r["race_id"]) & (results_df["driver_id"] == d_id), "points"]
            for race in df_points.items():
                final_points[f"y{i}"].append(race[1])
                final_points[f"x{i}"].append(r["race_id"])
     
    vals = []                       
    fig = go.Figure()
    
    for num in range(count):
        for v in final_points[f"x{num}"]:
            if v not in vals:
                vals.append(v)
        fig.add_trace(go.Bar(x=final_points[f"x{num}"], y=final_points[f"y{num}"], name=d_names[num], marker_color=scale[num])) 

    fig.update_layout(
            title=go.layout.Title(text="Total Points"),
            # yaxis = dict(
            #      side = "right"),
            xaxis = dict(
                tickangle = -45,
                tickmode = 'array',
                tickvals = vals,
                ticktext = race_names,
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

    # Custom colours for GO
    scale = ["#FF4B4B", "#FFA5A5", "#FFFFFF", "#666464", "#F76757"]

    if (len(drivers) != 0):
        metric_setup(year, drivers, standings_df, races_df, drivers_df, laps_df, c_df)
        final_pos_graph(year, results_df, races_df, driver_ids, drivers_df, scale)

        col1, col2 = st.columns(2, gap="large")
        points_graph(year, driver_ids, col2, races_df, results_df, scale, drivers_df)
    
        if (len(drivers) == 1):
            #TODO OLDER RACES AND DRIVER DATA NOT ALWAYS REGISTERING - MOSTLY LAPTIMES and D_ID
            #TODO MAKE GET RACES PER YEAR FOR EACH DRIVER MODULAR
            #TODO MULTI DRIVER SELECTIONS -IN PROG
            #TODO FASTEST LAP - CIRCUIT PRINT
            #TODO ORDER MULTIDRIVER DATA ON FINIHSING POS
            lap_times_graph(year, driver_ids, laps_df, races_df, col1)