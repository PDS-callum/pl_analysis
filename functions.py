import pandas as pd
import sqlite3
import requests
import random
import plotly.graph_objects as go

def df_to_db(df,database_file,table_name):
  conn = sqlite3.connect(database_file)
  df.to_sql(table_name, conn, if_exists='replace')
  conn.close()

def get_data(base_url,endpoint):
  url = f"{base_url}/{endpoint}"
  response = requests.get(url)
  return response.json()

def create_database(database_file):
  # Connect to the database (creates the file if it doesn't exist)
  conn = sqlite3.connect(database_file)

  # Close the connection (optional, but good practice)
  conn.close()

def id_to_name(x,df,name_col:str="player_name"):
  return df.query("entry == @x")[name_col].values[0]

def plot_timeseries(df,team_data_df):
  fig = go.Figure()
  for col in df:
    fig.add_trace(go.Scatter(
      y=df[col],
      name=id_to_name(col,team_data_df)
    ))
  return fig

def generate_hex_color(num_colors):
  """
  Generates a list of random hexadecimal color codes.

  Args:
    num_colors: The number of colors to generate.

  Returns:
    A list of hexadecimal color codes (strings).
  """
  color_list = []
  for _ in range(num_colors):
    hex_code = "#" + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)])
    color_list.append(hex_code)
  return color_list

def plot_timeseries_bar_by_gw(df:pd.DataFrame,colour_dict:dict,team_data_df):
  df = df.copy()
  df.columns = [id_to_name(col,team_data_df) for col in df.columns]
  df = df.T

  # Create figure
  fig = go.Figure()

  # Add traces, one for each slider step
  for i in df.columns:
    fig.add_trace(
      go.Bar(
        visible=False,
        x=df[i].sort_values(),
        y=df[i].sort_values().index,
        orientation='h',
        marker_color=[colour_dict[y] for y in df[i].sort_values().index]
        ))

  # Make first trace visible
  fig.data[0].visible = True

  # Create and add slider
  steps = []
  for i in range(len(fig.data)):
    step = dict(
      method="update",
      args=[{"visible": [False] * len(fig.data)},
      {"title": "Total by week: " + str(i+1)}],  # layout attribute
      )
    step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
    steps.append(step)
  sliders = [dict(
    active=0,
    currentvalue={"prefix": "GW: "},
    pad={"t": 50},
    steps=steps
  )]
  fig.update_layout(
    sliders=sliders
  )
  return fig

def get_timeseries(data,prop):
  df = pd.DataFrame()
  for id in data.keys():
    df[id] = [data[id]["current"][i][prop] for i in range(len(data[id]["current"]))]
  df["gw"] = list(range(1,len(df)+1))
  df = df.set_index("gw")
  return df

def get_weeks_first_last(df):
  first = []
  last = []
  for col in df.columns:
    first.append(df.index[(list(df[col].values).index(df[col].max()))])
    last.append(df.index[(list(df[col].values).index(df[col].min()))])
  df_out = pd.DataFrame(
    {
      "entry":list(df.index.values),
      "weeks_first":[first.count(x) for x in df.index.values],
      "weeks_last":[last.count(x) for x in df.index.values]
    }
  )
  return df_out