import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import numpy as np 
import pandas as pd 
import json
import plotly.express as px
import plotly.graph_objects as go
import plotly as py
from urllib.request import urlopen
from datetime import datetime, timedelta
import re



#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app = dash.Dash(__name__)

server = app.server

bg_color = "#202020"

def plot_choropleth_mapbox(map_data, val_json, val_loc, val_color, val_frame, val_title=''):
    max_color = max(map_data[val_color]) 
    fig = px.choropleth_mapbox(map_data, geojson=val_json, locations=val_loc, color=val_color,
                            color_continuous_scale="Viridis",
                            #color_discrete_sequence="peach",
                            range_color=(0, max_color),
                            mapbox_style="carto-darkmatter",
                            zoom=6, center = {"lat": 47.05048, "lon": 8.30635},
                            opacity=1,
                            height=500,
                            labels={'Confirmed Cases':'Cases'},
                            #animation_frame=val_frame,
                            template="plotly_dark",
                            title={'text':val_title},
                            #hover_name='Date',
                          )
    fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
    return fig

def plot_choropleth(map_data, val_json, val_loc, val_color, val_frame, val_title=''):
    max_color = max(map_data[val_color])
    bg_color = "#202020"
    fig = px.choropleth(map_data, geojson=val_json, locations=val_loc, color=val_color,
                            color_continuous_scale="Viridis",
                            range_color=(0, max_color),
                            center = {"lat": 47.05048, "lon": 8.30635},
                            height=500,
                            labels={'Confirmed Cases':'Cases'},
                            animation_frame=val_frame,
                            title={'text':val_title},
                            #hover_name='Date',
                          )
    fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0},
                        geo= {"visible": False,
                        "lataxis": {"range": [45.7845, 47.8406]},
                        "lonaxis": {"range": [5.5223, 10.5421]},
                        "projection": {"type": "transverse mercator"},
                        "bgcolor": bg_color,
                        },
                        paper_bgcolor=bg_color,
                        #template='plotly_dark',
                        font={"color": "AntiqueWhite"},
                        )
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
             )
    fig.update_xaxes(tickangle=-90, showticklabels=True, type = 'category')
    return fig

def format_diff_line(val_diff):
        return '{:+.0f}'.format(val_diff)
    
def format_pct_line(val_pct):
    return '{0:+.1%}'.format(val_pct)



ncumul_ind = ['ncumul_tested','ncumul_conf','current_hosp', 'current_icu', 'current_vent', 'ncumul_released','ncumul_deceased']
col_header = ['Date', 'Time', 'Canton', 'Tested', 'Confirmed Cases', 'Newly Hospitalised', 'Hospitalised', 'Intensive Care', 'Ventilator', 'Released', 'Fatalities', 'Source']
ncumul_ind = col_header[3:5]+col_header[6:11]
str_canton = 'abbreviation_canton_and_fl'

start_date='2020-03-06'


file = "https://raw.githubusercontent.com/flobrec/covid19/master/g2k20.geojson"
with urlopen(file) as response:
    canton_json = json.load(response)
df_cant_abv = pd.read_csv("https://raw.githubusercontent.com/flobrec/covid19/master/Cantons_ABV.csv", sep=",")
for i in range(0,26):
    canton_json['features'][i]['id'] = df_cant_abv.iloc[i]['Canton']
    

df_demographic = pd.read_csv("https://raw.githubusercontent.com/daenuprobst/covid19-cases-switzerland/master/demographics.csv", sep=',', error_bad_lines=False)      

link_openzh = "https://raw.githubusercontent.com/openZH/covid_19/master/COVID19_Fallzahlen_CH_total_v2.csv"

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
df_openzh_ch_growth.replace([np.inf, -np.inf], np.nan, inplace=True)

num_reporting = df_openzh_uns.groupby(axis=1,level=0).count().loc[:,'Confirmed Cases'].iloc[-1]
min_date = min(df_openzh_ch_diff.index)
max_date = max(df_openzh_ch_diff.index)

df_plot1 = df_openzh_ch[['Confirmed Cases', 'Fatalities', 'Released']].stack().reset_index()
df_plot1.columns = ['Date', 'Type', 'Reported Numbers']
fig1_ch = plot_line(df_plot1 ,'Date', 'Reported Numbers', 'Type','' ,'Confirmed Cases, Fatalities and Released from Hospital') 

df_plot2 = df_openzh_ch[['Hospitalised', 'Intensive Care', 'Ventilator']].stack().reset_index()
df_plot2.columns = ['Date', 'Type', 'Reported Numbers']
fig2_ch = plot_line(df_plot2 ,'Date', 'Reported Numbers', 'Type','' ,'Hospitalisation')

df_plot3 = df_openzh_ch_growth[['Confirmed Cases', 'Fatalities']].stack().reset_index()
df_plot3.columns = ['Date', 'Type', 'Percentage Changes']
fig3_ch = plot_line(df_plot3 ,'Date', 'Percentage Changes', 'Type','' ,'Percentage Changes')

df_choro = df_openzh_pad.replace(np.nan, 0)
df_choro.set_index('Date', drop=False, inplace=True)
df_choro = df_choro[start_date:].copy()
df_choro['DateTime'] = pd.to_datetime(df_choro['Date'], format='%Y-%m-%d')
df_choro['TimeStamp'] = df_choro['DateTime'].values.astype(np.int64) // 10 ** 9

fig1 = plot_choropleth(df_choro, canton_json, 'Canton', 'Confirmed Cases', 'Date', 'Confirmed Cases')

# fig1.show(renderer="browser")

df_choro_phk = df_openzh_phk_pad.replace(np.nan, 0)
df_choro_phk.set_index('Date', drop=False, inplace=True)
df_choro_phk = df_choro_phk[start_date:].copy()
df_choro_phk['DateTime'] = pd.to_datetime(df_choro_phk['Date'], format='%Y-%m-%d')
df_choro_phk['TimeStamp'] = df_choro_phk['DateTime'].values.astype(np.int64) // 10 ** 9

date_ticks = df_choro['TimeStamp'].unique()
date_labels = date_ticks[::4]

# fig4 = plot_bar(df_openzh_pad, 'Date', 'Confirmed Cases', 'Canton', 'Confirmed Cases', 'Confirmed Cases')
# fig5 = plot_line(df_openzh_phk_pad , 'Date', 'Confirmed Cases', 'Canton', 'Confirmed Cases', "Confirmed Cases Prevalence per 100'000")



app.layout = html.Div( children=[
    html.Div(className="grid-container", children=[
        html.Div(children=[
            html.Div(className="grid-title", children='Confirmed Cases'),
            html.P(df_openzh_ch['Confirmed Cases'].iloc[-1]),
            html.P(format_diff_line(df_openzh_ch_diff['Confirmed Cases'].iloc[-1]) +" (" + 
                   format_pct_line(df_openzh_ch_growth['Confirmed Cases'].iloc[-1]) + ")"),
            ]),
        html.Div(children=[
            html.Div(className="grid-title", children='Fatalities'),
            html.P(df_openzh_ch['Fatalities'].iloc[-1]),
            html.P(format_diff_line(df_openzh_ch_diff['Fatalities'].iloc[-1]) +" (" +
                   format_pct_line(df_openzh_ch_growth['Fatalities'].iloc[-1]) + ")"),
            ]),
        html.Div(children=[
            html.Div(className="grid-title", children='Released'),
            html.P(df_openzh_ch['Released'].iloc[-1]),
            html.P(format_diff_line(df_openzh_ch_diff['Released'].iloc[-1]) +" (" + 
                   format_pct_line(df_openzh_ch_growth['Released'].iloc[-1]) + ")"),
            ]),
        html.Div(children=[
            html.Div(className="grid-title", children='Hospitalised'),
            html.P(df_openzh_ch['Hospitalised'].iloc[-1]),
            html.P(format_diff_line(df_openzh_ch_diff['Hospitalised'].iloc[-1]) +" (" +
                   format_pct_line(df_openzh_ch_growth['Hospitalised'].iloc[-1]) + ")"),
            ]),
        html.Div(children=[
            html.Div(className="grid-title", children='Intensive Care'),
            html.P(df_openzh_ch['Intensive Care'].iloc[-1]),
            html.P(format_diff_line(df_openzh_ch_diff['Intensive Care'].iloc[-1]) +" (" +
                   format_pct_line(df_openzh_ch_growth['Intensive Care'].iloc[-1]) + ")"),
            ]),
        html.Div(children=[
            html.Div(className="grid-title", children='Ventilator'),
            html.P(df_openzh_ch['Ventilator'].iloc[-1]),
            html.P(format_diff_line(df_openzh_ch_diff['Ventilator'].iloc[-1]) +" (" +
                   format_pct_line(df_openzh_ch_growth['Ventilator'].iloc[-1]) + ")"),
            ]),
        html.Div(className="grid-one-col", children=[
            html.Div(className="grid-title", children='Updated Cantons'),
            html.P(num_reporting),
            ]),
        ]),
    html.Div(className="grid-container-nb", children=[
        html.Div(className="grid-item-1c", children=[
            html.H3('Charts Switzerland'),
            dcc.DatePickerRange(id='date-picker-range',
                                min_date_allowed=datetime.strptime(min_date, "%Y-%m-%d"),
                                max_date_allowed=datetime.strptime(max_date, "%Y-%m-%d")+timedelta(hours=23),
                                initial_visible_month=datetime.strptime(max_date, "%Y-%m-%d"),
                                start_date=datetime.strptime(start_date, "%Y-%m-%d"), 
                                end_date=datetime.strptime(max_date, "%Y-%m-%d"),
                                display_format="DD.MM.YYYY"
                                ),
            dcc.Graph(id="figure_ch1", ),
            dcc.Graph(id="figure_ch2", ),
            dcc.Graph(id="figure_ch3", ),
            ]),
       ]),
    html.Div(className="grid-container-nb", children=[
        html.Div(className="grid-item-1c", children=[
            html.H3('Charts Cantons'),
            ]),
        html.Div(className="grid-item-2c", children=[            
            html.Div(id= "dd_wrapper", children=[
                dcc.Dropdown(
                    id='choro-indicators',
                    options=[{'label': i, 'value': i} for i in ncumul_ind],
                    value='Confirmed Cases')
                ]),
            ]),
        html.Div(className="grid-item-1cr", children=[               
            html.Div(children=[            
                dcc.RadioItems(
                    id='report-type',
                    options=[{'label': i, 'value': i} for i in ['Total', "Prevalence per 100'000"]],
                    value='Total',
                    labelStyle={'display': 'inline-block'}),
                ]),
            ]),
       html.Div(className="grid-item-1c", children=[        
            dcc.Graph(id='graph-with-slider2', config={"staticPlot": True}),
            dcc.Slider(
                id='date-slider',
                min=df_choro['TimeStamp'].min(),
                max=df_choro['TimeStamp'].max(),
                value=df_choro['TimeStamp'].max(),
                #marks={str(date): datetime.fromtimestamp(date).strftime('%Y-%m-%d') for date in date_ticks},
                #marks={str(date): {'label': datetime.fromtimestamp(date).strftime('%d.%m.'), 'style': {"transform": "translateX(-50%) rotate(-90deg)"}} for date in date_ticks},
                marks={str(date): {'label': datetime.fromtimestamp(date).strftime('%d.%m.'), } for date in date_ticks},
                step=None,
                updatemode='drag',
                ),       
            # dcc.Graph(figure=fig1_ch),
            # dcc.Graph(figure=fig2_ch),
            # dcc.Graph(figure=fig3_ch),            
            ]), 
       ]),
    # html.Div(className="flex-container", children=[
    #     html.Div(className="flex-box-1", children=[
    #         html.H1('Charts Cantons'),
    #         #dcc.Graph(figure=fig1,),
    #         #dcc.Graph(figure=fig1, config={"staticPlot": True}),
    #         #dcc.Graph(figure=fig2),
    #         #dcc.Graph(figure=fig3),
    #         # dcc.Graph(figure=fig4),
    #         # dcc.Graph(figure=fig5),
    #         # dcc.Graph(figure=fig6),
    #         # dcc.Graph(figure=fig7),
    #         #dcc.Graph(figure=fig8),
    #         #dcc.Graph(figure=fig9),            
    #         ]),        
    #     ]),
    ])


@app.callback(
    Output('graph-with-slider2', 'figure'),
    [Input('choro-indicators', 'value'),
     Input('report-type', 'value'),
    Input('date-slider', 'value')])
def update_figure2(indicator_val, report_val , date_val):
    if report_val == 'Total':
        filtered_df = df_choro[df_choro['TimeStamp'] == date_val]
        max_val = max(df_choro[indicator_val])
    else:
        filtered_df = df_choro_phk[df_choro_phk['TimeStamp'] == date_val]
        max_val = max(df_choro_phk[indicator_val])

    return {
        'data': [{
            'type': 'choropleth',
            'geojson': canton_json,
            'locations': filtered_df['Canton'],
            'z': filtered_df[indicator_val],
            'coloraxis': 'coloraxis',
            },
            {
            'type': 'scattergeo',
            'geojson': canton_json,
            'locations': filtered_df['Canton'],
            'text': filtered_df[indicator_val],
            'texttemplate': '%{location}: %{text:.0f}',
            'mode': 'text',
            "textfont": {
                    "family": "Arial, sans-serif",
                    "size": 12,
                    "color": "Teal",
                    "weight": "bold",
                    },
            },
            ],
        'layout': {
            'coloraxis':{'colorscale': 'Peach', 'cmin':0, 'cmax':max_val},
            'geo': {
                "visible": False,
                "center": {"lat": 46.81, "lon": 8.22},
                "lataxis": {"range": [45.6, 47.9]},
                "lonaxis": {"range": [5.8, 10.6]},
                "projection": {"type": "transverse mercator"},
                "bgcolor": bg_color,
                },
            'paper_bgcolor': bg_color,
            'font': {
                "color": "AntiqueWhite"
                },
            'margin': {"r":0,"t":50,"l":0,"b":0},
            'height':600,
            },
        }

@app.callback(
    [Output('figure_ch1', 'figure'),
     Output('figure_ch2', 'figure'),
     Output('figure_ch3', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')])
def update_output(start_date, end_date):
    start_date = re.split('T| ', start_date)[0]
    end_date = re.split('T| ', end_date)[0]
    df_filtered = df_openzh_ch[start_date:end_date]
    df_filtered1 = df_filtered[['Confirmed Cases', 'Fatalities', 'Released']].stack().reset_index()
    df_filtered1.columns = ['Date', 'Type', 'Reported Numbers']
    fig1 = plot_line(df_filtered1 ,'Date', 'Reported Numbers', 'Type','' ,'Confirmed Cases, Fatalities and Released from Hospital')
    
    df_filtered2 = df_filtered[['Hospitalised', 'Intensive Care', 'Ventilator']].stack().reset_index()
    df_filtered2.columns = ['Date', 'Type', 'Reported Numbers']
    fig2 = plot_line(df_filtered2 ,'Date', 'Reported Numbers', 'Type','' ,'Hospitalisation')

    df_filtered_growth = df_openzh_ch_growth[start_date:end_date]
    df_filtered3 = df_filtered_growth[['Confirmed Cases', 'Fatalities']].stack().reset_index()
    df_filtered3.columns = ['Date', 'Type', 'Percentage Changes']
    fig3 = plot_line(df_filtered3 ,'Date', 'Percentage Changes', 'Type','' ,'Percentage Changes')

    return fig1, fig2, fig3
    # string_prefix = 'You have selected: '
    # if start_date is not None:
    #     start_date = dt.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d')
    #     start_date_string = start_date.strftime('%B %d, %Y')
    #     string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
    # if end_date is not None:
    #     end_date = dt.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d')
    #     end_date_string = end_date.strftime('%B %d, %Y')
    #     string_prefix = string_prefix + 'End Date: ' + end_date_string
    # if len(string_prefix) == len('You have selected: '):
    #     return 'Select a date to see it displayed here'
    # else:
    #     return string_prefix


if __name__ == '__main__':
    app.run_server(debug=False, use_reloader=True)