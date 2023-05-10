import os
import json
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash import dash_table
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import plotly.express as px
import plotly.io as pio
import folium
from folium import Map, Marker, Popup, IFrame
from folium import Icon
import branca

# Set default plotly theme
pio.templates.default = 'plotly_dark'

# Read data
df = pd.read_csv('data/VTmoviesCoords.csv')
year_min = df['Year'].min()
year_max = df['Year'].max()

# Read GeoJSON file
with open('vermont-county-boundaries.geojson', 'r') as f:
    vt_geojson = json.load(f)

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.SLATE],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}])
server = app.server

def create_folium_map(filtered_df):
    vt_map = Map(location=[filtered_df['Latitude'].mean(), filtered_df['Longitude'].mean()], zoom_start=7, control_scale=True)

    # Add state and county borders
    folium.GeoJson(
        vt_geojson,
        style_function=lambda x: {'fillColor': 'transparent', 'color': 'blue' if 'cntyname' not in x['properties'] else 'green', 'weight': 2 if 'cntyname' not in x['properties'] else 1.5}
    ).add_to(vt_map)

    for index, row in filtered_df.iterrows():
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 16px;">
            <h4><b>{row['Title']}</b></h4>
            <p>Year: {row['Year']}<br>
            Town: {row['Town']}</p>
            <a href="{row['URL']}" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/IMDB_Logo_2016.svg/64px-IMDB_Logo_2016.svg.png" width="70" height="35" alt="IMDb"></a>
            <p style="font-size: 14px; color: #666;"><i>Click the link to visit the movie's IMDb page.</i></p>
        </div>
        """
        iframe = IFrame(html=popup_html, width=300, height=180)
        popup = Popup(iframe, max_width=300)
        Marker(location=[row['Latitude'], row['Longitude']], popup=popup).add_to(vt_map)

    return vt_map

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1('Movies Filmed in Vermont - Dashboard',
                        className="text-center text-primary, mb-4"),
                width=12)
    ]),
    dbc.Row([
        dbc.Col(html.H5('Interactive Map of Filming Locations', className="text-center"))
    ]),
    dbc.Row([
        dbc.Col(html.Div([
            dcc.Tabs(id='tabs', children=[
                dcc.Tab(label='Map', children=[
                    html.Iframe(id='map', width='100%', height='600')
                ]),
                dcc.Tab(label='DataTable and Chart', children=[
                    dbc.Row([
                        dbc.Col(
                            dcc.Graph(
                                id='graph',
                                figure={
                                                                        'data': [
                                        {'x': df['Title'],
                                         'y': df['Box Office Gross'], 'marker': {"color": '#005710'}, 'type': 'bar'},
                                    ],
                                }),
                            width=12, lg=6),
                        dbc.Col(
                            html.Div(
                                dash_table.DataTable(id='table-container',
                                                     columns=[{'name': col, 'id': col}
                                                              for col in df.columns],
                                                     data=df.to_dict('records'),
                                                     style_cell={
                                                         'font_family': 'Arial',
                                                         'padding': '1.rem',
                                                         'backgroundColor': '#f4f4f2',
                                                         'headers': True
                                                     },
                                                     style_header={
                                                         'backgroundColor': 'white',
                                                         'fontWeight': 'bold',
                                                         'backgroundColor': 'rgb(30, 30, 30)',
                                                         'color': 'white',
                                                         'fontWeight': 'bold'

                                                     },
                                                     style_data={
                                                         'backgroundColor': 'rgb(50, 50, 50)',
                                                         'color': 'white'
                                                     },
                                                     style_table={
                                                         'maxHeight': '400px',
                                                         'maxWidth': '1900px',
                                                         'overflowX': 'scroll',
                                                         'overflowY': 'scroll'
                                                     })),
                            width=12, lg=6)
                    ]),
                ]),
            ]),
        ]), width={'size': 10, 'offset': 1})
    ]),
    dbc.Row([
        dbc.Col(html.H6('Range-Slider: Filter the years.', className="text-center"))
    ]),
    dbc.Row([
        dbc.Col(dcc.RangeSlider(id='year-slider',
                                min=year_min,
                                max=year_max,
                                value=[year_min, year_max],
                                marks={i: str(i) for i in range(year_min, year_max+1)}),
                )
    ]),
], fluid=True)

@app.callback(
    Output('graph', 'figure'),
    Input('year-slider', 'value')
)
def update_bar_chart(selected_years):
    filtered_df = df[(df['Year'] >= selected_years[0]) &
                     (df['Year'] <= selected_years[1])]
    figure = px.bar(filtered_df, x='Title', y='Box Office Gross')
    return figure

@app.callback(
    Output('map', 'srcDoc'),
    Input('year-slider', 'value')
)
def update_map(selected_years):
    filtered_df = df[(df['Year'] >= selected_years[0]) &
                     (df['Year'] <= selected_years[1])]
    vt_map = create_folium_map(filtered_df)
    return vt_map.get_root().render()

if __name__ == '__main__':
    app.run_server(debug=True)

