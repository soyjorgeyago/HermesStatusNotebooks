# CONFIG SECTION
file = "2017-06-14_15.30.15 (2n1b2r)"
yAxis1 = 'CurrentDriversDelay'
yAxis2 = 'ActiveDrivers'
from_index = 0


# DATA PROCESS
import pandas as pd

from plotly.graph_objs import *
from plotly.offline import init_notebook_mode, plot, iplot

init_notebook_mode(connected=True)

df = pd.read_csv("CSV_Files/" + file + ".csv", sep=";", parse_dates=["Time"])

df1 = df.set_index(["PcKey", "Timestamp"])
df1 = df1.sort_index()

list_df = []
pc_ids = df["PcKey"].unique()  # give me all the PcKeys without duplicates
pc_ids = pc_ids[from_index:]

dfs_yAxis2 = []

# for each pc
for pc_id in pc_ids:
    df2 = df1.loc[pc_id, ['Time', yAxis1]]  # build a dataframe per vehicle
    df2 = df2.set_index("Time")  # index by time
    df2 = df2.resample('1S').mean()  # add rows with 1s difference
    df2 = df2.round(0)

    pc_info = {"name": pc_id, "delay": df2[yAxis1]}  # build a dictionary
    list_df.append(pc_info)

    df3 = df1.loc[pc_id, ['Time', yAxis2]]  # build a dataframe per vehicle
    df3 = df3.set_index("Time")  # index by time
    df3 = df3.resample('1S').mean()
    df3 = df3.round(0)
    df3 = df3.bfill()
    dfs_yAxis2.append(df3)


# DATA AGGREGATION
aux = len(dfs_yAxis2) - 1
df_total = dfs_yAxis2[aux]
while aux >= 0:
    df_total = (df_total.reindex_like(dfs_yAxis2[aux]).fillna(0) + dfs_yAxis2[aux].fillna(0)) \
        .fillna(0)
    aux -= 1

df_total = {"name": yAxis2, "drivers": df_total[yAxis2]}


# PLOT RESULTS
import plotly.graph_objs as go
import numpy as np

date = []
traces = []
menu = []
index = 0

for pc_data in list_df:
    traces.append(go.Scatter(x=pc_data["delay"].index, y=pc_data["delay"], name=pc_data["name"],
                             mode='lines+markers', connectgaps=True, opacity=0.8))

traces.append(go.Scatter(x=df_total["drivers"].index, y=df_total["drivers"],
                         name=df_total["name"], mode='lines+markers', connectgaps=True,
                         opacity=0.8, yaxis='y2'))

menu.append(dict(args=['visible', [True] * (len(list_df))], label='All', method='restyle'))
zeros = np.zeros(len(list_df))

for index, pc_id in enumerate(list_df):
    array = [False] * (len(list_df))
    array[index] = True
    menu.append(dict(args=['visible', array], label=pc_id["name"], method='restyle'))

layout = Layout(
    title="Evolución temporal, file: " + file,
    updatemenus=list([
        dict(
            x=-0.15,
            y=1,
            yanchor='top',
            buttons=list(menu),

        )
    ]),
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=20,
                     label='20s',
                     step='second',
                     stepmode='backward'),
                dict(count=1,
                     label='1m',
                     step='minute',
                     stepmode='backward'),
                dict(step='all')
            ])
        ),
        rangeslider=dict(visible=False),
        type='date'
    ),
    yaxis=dict(
        title=yAxis1
    ),
    yaxis2=dict(
        title=yAxis2,
        titlefont=dict(
            color='rgb(148, 103, 189)'
        ),
        tickfont=dict(
            color='rgb(148, 103, 189)'
        ),
        overlaying='y',
        side='right'
    ),
    autosize=True,
)

fig = Figure(data=traces, layout=layout)
# iplot(fig)    # Looks good, doesnt work xD
plot(fig)
