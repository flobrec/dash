import os

import dash
import dash_core_components as dcc
import dash_html_components as html

import numpy as np 
import pandas as pd 
import json
import plotly.express as px
from urllib.request import urlopen

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app = dash.Dash(__name__)

server = app.server

def my_function(x):
    return 5*x

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


file = "https://raw.githubusercontent.com/flobrec/covid19/master/g2k20.geojson"
with urlopen(file) as response:
    cantons = json.load(response)
df_cant_abv = pd.read_csv("https://raw.githubusercontent.com/flobrec/covid19/master/Cantons_ABV.csv", sep=",")
for i in range(0,26):
    cantons['features'][i]['id'] = df_cant_abv.iloc[i]['Canton']
    

df_demographic = pd.read_csv("https://raw.githubusercontent.com/daenuprobst/covid19-cases-switzerland/master/demographics.csv", sep=',', error_bad_lines=False)      

df_orig = pd.read_csv("https://raw.githubusercontent.com/daenuprobst/covid19-cases-switzerland/master/covid19_cases_switzerland.csv", sep=',', index_col='Date', error_bad_lines=False)
df_orig_fat = pd.read_csv("https://raw.githubusercontent.com/daenuprobst/covid19-cases-switzerland/master/covid19_fatalities_switzerland.csv", sep=',', index_col='Date', error_bad_lines=False)

df_orig = df_orig.fillna(method='pad')
df_orig_fat = df_orig_fat.fillna(method='pad')
df_orig_fat = df_orig_fat.replace(0, np.nan)

df = df_orig.stack().reset_index().rename(columns={'level_0':'Date','level_1':'Canton', 0:'Cases'})
df_cfr = df_orig_fat.div(df_orig)
df_cfr_stack = df_cfr.stack().reset_index().rename(columns={'level_0':'Date','level_1':'Canton', 0:'CFR'})

df_ch = df[df['Canton']=='CH']
df_cantons = df[df['Canton']!='CH']
df_cantons = pd.merge(df_cantons, df_cant_abv[['id','Canton']], on='Canton', how='left')
#df_cantons = pd.merge(df_cantons, ch_map[['id','Canton']], on='Canton', how='left')
df_cantons = pd.merge(df_cantons, df_demographic[['Canton','Population']], on='Canton', how='left')
df_cantons['CasesPer100k'] = round(df_cantons['Cases'] / df_cantons['Population'] * 100000, 2)

df_ch_diff_pct = df_ch['Cases'].pct_change()
avg_diff_pct = (df_ch.iloc[-1]['Cases']/df_ch.iloc[0]['Cases'])**(1/(len(df_ch)-1))-1
time_dbl = time_dbl = np.log(2)/np.log(1+avg_diff_pct)

#bar charts
bar_data = df_cantons.groupby(['Canton', 'Date'])['Cases'].sum().reset_index().sort_values('Date', ascending=True)
# cases per 100k
bar_data_pc = df_cantons.groupby(['Canton', 'Date'])['CasesPer100k'].sum().reset_index().sort_values('Date', ascending=True)

max_color = max(df_cantons['Cases'])
max_color_100k = max(df_cantons['CasesPer100k'])

fig1 = plot_choropleth(df_cantons, cantons, 'Canton', 'Cases', 'Date')
fig2 = plot_choropleth(df_cantons, cantons, 'Canton', 'CasesPer100k', 'Date')
fig3 = plot_bar(bar_data, 'Date', 'Cases', 'Canton','Cases')
fig4 = plot_bar(bar_data_pc, 'Date', 'CasesPer100k', 'Canton', 'CasesPer100k')
fig5 = plot_line(df_cfr_stack, 'Date', 'CFR', 'Canton','CFR')
 
#fig.update_yaxes(type="log")



app.layout = html.Div( children=[
    html.Div(children=[
        html.H2(children='Evolution of Cases'),
        dcc.Graph(id='choropleth', figure=fig1)]),
    html.Div(children=[
        html.H2(children='Evolution of Cases per 100k'),
        dcc.Graph(id='choropleth2', figure=fig2)]),
    html.Div(children=[
        html.H2(children='Cases by Canton'),
        dcc.Graph(id='bar', figure=fig3)]),
    html.Div(children=[
        html.H2(children='Cases by Canton per 100k'),
        dcc.Graph(id='bar2', figure=fig4)]),
    html.Div(children=[
        html.H2(children='Case Fatality Rate'),
        dcc.Graph(id='line', figure=fig5)])
])



if __name__ == '__main__':
    app.run_server(debug=True)