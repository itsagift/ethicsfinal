import pandas as pd
import geopandas as gpd
import json
import dill
import bokeh

from bokeh.io import output_file, show, output_notebook, export_png
from bokeh.models import ColumnDataSource, GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.plotting import figure
from bokeh.palettes import brewer

import panel as pn
import panel.widgets as pnw

import random
import os
import requests
from dotenv import load_dotenv
import numpy as np

def get_geo_data():
    car_data = gpd.read_file("data/acs2023_5yr_B25044_86000US07206.geojson")
    nbh_data = gpd.read_file("data/custom-pedia-cities-nyc-Mar2018 (1).geojson")
    
    
    car_data['no_vehicle'] = car_data['B25044003'] + car_data['B25044010']
    car_data['pct_no_vehicle'] = (car_data['no_vehicle'] / car_data['B25044001']) * 100
    car_data['pct_vehicle'] = 100 - (car_data['pct_no_vehicle'])

    car_data = car_data[car_data['name'].str.startswith('1')]
    car_data.rename(columns={'B25044001': 'households'}, inplace=True)
    car_data = car_data[car_data['households'] > 0]
    car_data = car_data.to_crs(epsg=3857)
    nbh_data = nbh_data.to_crs(epsg=3857)
    
    return (car_data, nbh_data)
def get_live_data():
    livefeed_json = requests.get(url="https://gbfs.citibikenyc.com/gbfs/en/station_status.json")
    livefeed_data = livefeed_json.json()
    items_df = pd.DataFrame(livefeed_data['data']['stations'])
    return items_df

def get_citibike_data():
    # get live data from citibike json
    livefeed_json = requests.get(url="https://gbfs.citibikenyc.com/gbfs/en/station_status.json")
    livefeed_data = livefeed_json.json()
    items_df = pd.DataFrame(livefeed_data['data']['stations'])

    # get static station data from citibike json
    station_json = requests.get(url="https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_information.json")
    station_data = station_json.json()
    # clean and read static data
    station_df = pd.DataFrame(station_data['data']['stations'])
    station_df.rename(columns={'name': 'station_name'})
    return (items_df, station_df)

def pandas_to_geojson(gdf):
    geojson_data = json.loads(gdf.to_json())
    geosource = GeoJSONDataSource(geojson=json.dumps(geojson_data))
    return geosource