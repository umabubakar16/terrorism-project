import random
import textwrap
import datetime as dt 
import dash
from dash import Dash, html, dcc, callback, Output, Input
import plotly.graph_objs as go
import pandas as pd

# Load your terrorism data
terrorism = pd.read_csv('data/terrorism.csv', encoding='latin-1', low_memory=False,
                        usecols=['iyear', 'imonth', 'iday', 'provstate', 'city', 'longitude', 'latitude',
                                 'nkill', 'nwound', 'summary', 'target1', 'gname'])

terrorism = terrorism[terrorism['imonth'] != 0]
terrorism['day_clean'] = [15 if x == 0 else x for x in terrorism['iday']]
terrorism['date'] = [dt.datetime(y, m, d) for y, m, d in zip(terrorism['iyear'], terrorism['imonth'], terrorism['day_clean'])]

app = dash.Dash(__name__)

# Get unique values for 'provstate' and 'city' for dropdown options
provstate_options = [{'label': state, 'value': state} for state in sorted(terrorism['provstate'].unique())]
city_options = [{'label': city, 'value': city} for city in sorted(terrorism['city'].unique())]

layout = html.Div([
    html.Br(),
    html.H3('Terrorism Data: 1970 - 2016'),
    dcc.Graph(id='map',
              config={'displayModeBar': False}),
    html.Div([
        dcc.RangeSlider(id='years',
                        min=1970,
                        max=2016,
                        dots=True,
                        value=[2010, 2016],
                        marks={str(yr): "'" + str(yr)[2:] for yr in range(1970, 2017)}),
        html.Br(), html.Br(),
    ], style={'width': '75%', 'margin-left': '12%', 'background-color': '#eeeeee'}),
    html.Div([
        dcc.Dropdown(id='provstate-dropdown',
                     multi=True,
                     value=[''],
                     placeholder='Select Province/State',
                     options=provstate_options),
        dcc.Dropdown(id='city-dropdown',
                     multi=True,
                     value=[''],
                     placeholder='Select City',
                     options=city_options)
    ], style={'width': '50%', 'margin-left': '25%', 'background-color': '#eeeeee'}),

    dcc.Graph(id='by_year',
              config={'displayModeBar': False}),
], style={'background-color': '#eeeeee', 'font-family': 'Palatino'})

@app.callback(Output('by_year', 'figure'),
             [Input('provstate-dropdown', 'value'), Input('city-dropdown', 'value'), Input('years', 'value')])
def annual_barchart(selected_provstates, selected_cities, selected_years):
    df = terrorism[
        terrorism['provstate'].isin(selected_provstates) &
        terrorism['city'].isin(selected_cities) &
        terrorism['iyear'].between(selected_years[0], selected_years[1])
    ]
    df = df.groupby(['iyear'], as_index=False)['date'].count()
    
    return {
        'data': [go.Bar(x=df['iyear'],
                        y=df['date'])],
        'layout': go.Layout(title='Yearly Terrorist Attacks',
                            plot_bgcolor='#eeeeee',
                            paper_bgcolor='#eeeeee',
                            font={'family': 'Palatino'})
    }

if __name__ == '__main__':
    app.run_server(debug=True)
