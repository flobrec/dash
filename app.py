import os

import dash
import dash_core_components as dcc
import dash_html_components as html

import numpy as np 
import pandas as pd 
import json
import plotly.express as px
from urllib.request import urlopen

import functions as func


#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app = dash.Dash(__name__)

server = app.server

ncumul_ind = ['ncumul_tested','ncumul_conf','ncumul_hosp', 'ncumul_ICU', 'ncumul_vent', 'ncumul_released','ncumul_deceased']
col_header = ['Date', 'Time', 'Canton', 'Tested', 'Confirmed Cases', 'Hospitalised', 'Intensive Care', 'Ventilator', 'Released', 'Fatalities', 'Source']
ncumul_ind = col_header[3:10]
str_canton = 'abbreviation_canton_and_fl'
start_date='2020-03-06'

file = "https://raw.githubusercontent.com/flobrec/covid19/master/g2k20.geojson"
with urlopen(file) as response:
    canton_json = json.load(response)
df_cant_abv = pd.read_csv("https://raw.githubusercontent.com/flobrec/covid19/master/Cantons_ABV.csv", sep=",")
for i in range(0,26):
    canton_json['features'][i]['id'] = df_cant_abv.iloc[i]['Canton']
    

df_demographic = pd.read_csv("https://raw.githubusercontent.com/daenuprobst/covid19-cases-switzerland/master/demographics.csv", sep=',', error_bad_lines=False)      

link_openzh = "https://raw.githubusercontent.com/openZH/covid_19/master/COVID19_Fallzahlen_CH_total.csv"
df_openzh = pd.read_csv(link_openzh, sep= ',')
df_openzh.columns = col_header
df_openzh = df_openzh[df_openzh['Canton']!='FL']    # remove FL
#df_openzh['date']= pd.to_datetime(df_openzh['date'], format="%Y-%m-%d")

df_openzh.sort_values(by=['Date'], ascending=True, inplace=True)

index = ncumul_ind.copy()
index.insert(0,'Canton')
index.insert(0,'Date')
df_openzh_mi = df_openzh[index]
df_openzh_mi = df_openzh_mi.set_index(['Date', 'Canton'])     # multi index
df_openzh_uns = df_openzh_mi.unstack('Canton')                # unstack
df_openzh_uns_pad = df_openzh_uns.fillna(method='pad')          # pad nan
df_openzh_pad = df_openzh_uns_pad.stack(dropna=False)                       # stack
df_openzh_pad.reset_index(inplace=True)
df_openzh_pad.sort_values(by=['Date'], ascending=True, inplace=True)

df_openzh_diff = df_openzh_uns_pad.diff()
df_openzh_growth = df_openzh_uns_pad.pct_change()

df_openzh_phk_pad = pd.merge(df_openzh_pad, df_demographic[['Canton','Population']], left_on='Canton', right_on='Canton',how='left')
df_openzh_phk_pad[ncumul_ind] = round(df_openzh_phk_pad[ncumul_ind].div(df_openzh_phk_pad['Population'],axis=0)*100000,2)

df_openzh_pad['CFR'] = round(df_openzh_pad['Fatalities'].div(df_openzh_pad['Confirmed Cases']), 3)

df_openzh_ch = df_openzh_uns_pad.groupby(axis=1,level=0).sum()
df_openzh_ch_diff = df_openzh_ch.diff()
df_openzh_ch_growth = df_openzh_ch.pct_change()

num_reporting = df_openzh_uns.groupby(axis=1,level=0).count().loc[:,'Confirmed Cases'].iloc[-1]

df_plot1 = df_openzh_ch[['Confirmed Cases', 'Fatalities', 'Released']].stack().reset_index()
df_plot1.columns = ['Date', 'Type', 'Reported Numbers']
fig1_ch = func.plot_line(df_plot1 ,'Date', 'Reported Numbers', 'Type','' ,'Confirmed Cases, Fatalities and Released from Hospital') 

df_plot2 = df_openzh_ch[['Hospitalised', 'Intensive Care', 'Ventilator']].stack().reset_index()
df_plot2.columns = ['Date', 'Type', 'Reported Numbers']
fig2_ch = func.plot_line(df_plot2 ,'Date', 'Reported Numbers', 'Type','' ,'Hospitalisation') 

df_choro_case = df_openzh_pad.replace(np.nan, 0)
df_choro_phk = df_openzh_phk_pad.replace(np.nan, 0)
df_choro_fat = df_openzh_pad.replace(np.nan, 0)
fig1 = func.plot_choropleth(df_choro_case[['Date', 'Canton', 'Confirmed Cases']], canton_json, 'Canton', 'Confirmed Cases', 'Date', 'Confirmed Cases')
fig2 = func.plot_choropleth(df_choro_phk, canton_json, 'Canton', 'Confirmed Cases', 'Date', "Confirmed Cases Prevalence per 100'000")
fig3 = func.plot_choropleth(df_choro_fat, canton_json, 'Canton', 'Fatalities', 'Date', 'Fatalities')
fig4 = func.plot_bar(df_openzh_pad, 'Date', 'Confirmed Cases', 'Canton', 'Confirmed Cases', 'Confirmed Cases')
fig5 = func.plot_line(df_openzh_phk_pad , 'Date', 'Confirmed Cases', 'Canton', 'Confirmed Cases', "Confirmed Cases Prevalence per 100'000")
fig6 = func.plot_bar(df_openzh_pad , 'Date', 'Fatalities', 'Canton', 'Fatalities', 'Fatalities')
fig7 = func.plot_line(df_openzh_pad, 'Date', 'CFR', 'Canton','CFR', 'Case Fatality Ratio')

df_plot1 = df_openzh_ch[['Confirmed Cases', 'Fatalities', 'Released']].stack().reset_index()
df_plot1.columns = ['Date', 'Type', 'Reported Numbers']
fig1_ch = func.plot_line(df_plot1 ,'Date', 'Reported Numbers', 'Type','' ,'Confirmed Cases, Fatalities and Released from Hospital') 

df_plot2 = df_openzh_ch[['Hospitalised', 'Intensive Care', 'Ventilator']].stack().reset_index()
df_plot2.columns = ['Date', 'Type', 'Reported Numbers']
fig2_ch = func.plot_line(df_plot2 ,'Date', 'Reported Numbers', 'Type','' ,'Hospitalisation') 


app.layout = html.Div( children=[
    html.Div(className="flex-container", children=[
        html.Div(className="flex-box-3", children=[
            html.P('Confirmed Cases'),
            html.P(df_openzh_ch['Confirmed Cases'].iloc[-1]),
            html.P(func.format_diff_line(df_openzh_ch_diff['Confirmed Cases'].iloc[-1])),
            html.P(func.format_pct_line(df_openzh_ch_growth['Confirmed Cases'].iloc[-1])),
            ]),
        html.Div(className="flex-box-3", children=[
            html.P('Fatalities'),
            html.P(df_openzh_ch['Fatalities'].iloc[-1]),
            html.P(func.format_diff_line(df_openzh_ch_diff['Fatalities'].iloc[-1])),
            html.P(func.format_pct_line(df_openzh_ch_growth['Fatalities'].iloc[-1])),
            ]),
        html.Div(className="flex-box-3", children=[
            html.P('Released'),
            html.P(df_openzh_ch['Released'].iloc[-1]),
            html.P(func.format_diff_line(df_openzh_ch_diff['Released'].iloc[-1])),
            html.P(func.format_pct_line(df_openzh_ch_growth['Released'].iloc[-1])),
            ]),
        ]),
    html.Div(className="flex-container", children=[
        html.Div(className="flex-box-3", children=[
            html.P('Hospitalised'),
            html.P(df_openzh_ch['Hospitalised'].iloc[-1]),
            html.P(func.format_diff_line(df_openzh_ch_diff['Hospitalised'].iloc[-1])),
            html.P(func.format_pct_line(df_openzh_ch_growth['Hospitalised'].iloc[-1])),
            ]),
        html.Div(className="flex-box-3", children=[
            html.P('Intensive Care'),
            html.P(df_openzh_ch['Intensive Care'].iloc[-1]),
            html.P(func.format_diff_line(df_openzh_ch_diff['Intensive Care'].iloc[-1])),
            html.P(func.format_pct_line(df_openzh_ch_growth['Intensive Care'].iloc[-1])),
            ]),
        html.Div(className="flex-box-3", children=[
            html.P('Ventilator'),
            html.P(df_openzh_ch['Ventilator'].iloc[-1]),
            html.P(func.format_diff_line(df_openzh_ch_diff['Ventilator'].iloc[-1])),
            html.P(func.format_pct_line(df_openzh_ch_growth['Ventilator'].iloc[-1])),
            ]),
        ]),
    html.Div(className="flex-container", children=[
        html.Div(className="flex-box-1", children=[
            html.P('Updated Cantons'),
            html.P(num_reporting),
            ]),
        ]),
    html.Div(className="flex-container", children=[
        html.Div(className="flex-box-1", children=[
            html.P('Charts Switzerland'),
            dcc.Graph(figure=fig1_ch),
            dcc.Graph(figure=fig2_ch),
            ]),
        ]),
    html.Div(className="flex-container", children=[
        html.Div(className="flex-box-1", children=[
            html.P('Charts Cantons'),
            #dcc.Graph(figure=fig1),
            #dcc.Graph(figure=fig2),
            #dcc.Graph(figure=fig3),
            dcc.Graph(figure=fig4),
            dcc.Graph(figure=fig5),
            dcc.Graph(figure=fig6),
            dcc.Graph(figure=fig7),
            ]),        
        ]),
     
      
    #     html.H2(children='Evolution of Cases'),
    #     dcc.Graph(id='choropleth', figure=fig1)]),
    # html.Div(children=[
    #     html.H2(children='Evolution of Cases per 100k'),
    #     dcc.Graph(id='choropleth2', figure=fig2)]),
    # html.Div(children=[
    #     html.H2(children='Cases by Canton'),
    #     dcc.Graph(id='bar', figure=fig3)]),
    # html.Div(children=[
    #     html.H2(children='Cases by Canton per 100k'),
    #     dcc.Graph(id='bar2', figure=fig4)]),
    # html.Div(children=[
    #     html.H2(children='Case Fatality Rate'),
    #     dcc.Graph(id='line', figure=fig5)])

])

if __name__ == '__main__':
    app.run_server(debug=True)