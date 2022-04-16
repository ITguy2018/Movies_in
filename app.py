# Import libraries
import dash
from dash import Dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash import Dash, dash_table
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import plotly.express as px
# --------------------------------------------------------------------------------------------
# Left off here, trying to get map(iframe) to be beside datatable !!!!!!!!!!!!!

df = pd.read_csv('data/VTmoviesCoords.csv')
year_min = df['Year'].min()
year_max = df['Year'].max()


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.MINTY],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}])
server = app.server


# Layout: With Bootstrap
# --------------------------------------------------------------------------------------------
# Start the layout of app
# Put title and format it in column
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1('Movies Filmed in Vermont - Dashboard',
                        className="text-center text-primary, mb-4"),
                width=12)

    ]),
    # Title above the map
    dbc.Row([
        dbc.Col(html.H5('Interactive Map of Filming Locations'))




    ]),
    # html Iframe loading in the map file
    dbc.Row([
        dbc.Col(html.Div([html.Iframe(id='map', srcDoc=open(
            'data/Updated_Movies_In_Vermont.html', 'r').read(), width='99%', height='620')], style={'width': '95%', 'display': 'inline-block'
                                                                                            }), style={'width': '49%', 'display': 'inline-block'}),
        # New column where the graph will be place - beside the map
        dbc.Col(
            # Create a graph and choose desired parameters
            dcc.Graph(
                id='graph',
                figure={
                    'data': [
                        {'x': df['Title'],
                         'y': df['Box Office Gross'], 'marker': {"color": '#005710'}, 'type': 'bar'},
                    ],
                    'layout': {
                        'title': 'Movie Titles | Box Office numbers',
                        'height': 700,
                        'width': 910,

                    },

                }, style={'width': '49%', 'display': 'inline-block'}),


        )
    ]),
    # Small header for the range slider
    dbc.Row([
        dbc.Col(html.H6('Range-Slider: Use this to filter the data below.'))

    ]),
    # Range-slider
    # Provides a method to be able to filter years based on a range
    dbc.Row([
        dbc.Col(dcc.RangeSlider(id='year-slider',
                                min=year_min,
                                max=year_max,
                                value=[year_min, year_max],
                                marks={i: str(i) for i in range(year_min, year_max+1)}),

                )


    ]),



    dbc.Row([
            dbc.Col(html.Div(
                # Datatable of the actual dataset
                # Use range slider to view films in particular desired filming Years
                dash_table.DataTable(id='table-container',
                                     columns=[{'name': col, 'id': col}
                                              for col in df.columns],
                                     data=df.to_dict('records'),
                                     # CSS code for formatting
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
                                     })))
            ])

], fluid=True)

# Call-back components
# --------------------------------------------------------------------------------------------


@ app.callback(
    Output('table-container', 'children'),
    Input('year-slider', 'value')
)
def update_table(value):

    return str(value)

# Call back function to connect the datatable and range slider
@ app.callback(
    Output('table-container', 'data'),
    Input('year-slider', 'value')
)
# Function for updating the datatable
def update_datable(selected_years):
    filtered_df = df[(df['Year'] >= selected_years[0]) &
                     (df['Year'] <= selected_years[1])]
    return filtered_df.to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=False)
