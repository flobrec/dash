import os

import dash
import dash_core_components as dcc
import dash_html_components as html

import numpy as np 
import pandas as pd 
import json
import plotly.express as px
from urllib.request import urlopen


def plot_choropleth(map_data, val_json, val_loc, val_color, val_frame):
    max_color = max(map_data[val_color]) 
    fig = px.choropleth_mapbox(map_data, geojson=val_json, locations=val_loc, color=val_color,
                            color_continuous_scale="peach",
                            range_color=(0, max_color),
                            mapbox_style="carto-darkmatter",
                            zoom=6, center = {"lat": 47.05048, "lon": 8.30635},
                            opacity=0.5,
                            height=500,
                            #labels={'Cases':'Confirmed cases'},
                            animation_frame=val_frame,
                            template="plotly_dark",
                            #hover_name='Date'
                          )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

def plot_bar(bar_data, val_x, val_y, val_color, val_text, val_title='',val_scale='linear'):
    fig = px.bar(bar_data, x=val_x, y=val_y,
             color=val_color, text=val_text,
             orientation='v',
             height=500,
             title= val_title,
             template="plotly_dark",
             color_discrete_sequence= px.colors.cyclical.Phase,
             #hover_name='Canton'
             )
    # fig.update_traces(hovertemplate = '<b>Canton: %{hovertext}</b><br>'
    #           +'Date: %{x}<br>'
    #           +'Cases: %{y:.0f}'
    #           )
    fig.update_xaxes(tickangle=-90, showticklabels=True, type = 'category')
    fig.update_yaxes(type=val_scale)
    return fig

def plot_line(data, val_x, val_y, val_color, val_text='', val_title=''):
    fig = px.line(data, x=val_x, y=val_y,
             color=val_color,
             #text=val_text,
             #orientation='v',
             height=500,
             title=val_title,
             template="plotly_dark",
             color_discrete_sequence= px.colors.cyclical.Phase,
             #hover_name='Canton'
             )
    fig.update_xaxes(tickangle=-90, showticklabels=True, type = 'category')
    return fig