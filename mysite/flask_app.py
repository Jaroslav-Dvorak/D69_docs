import locale
import platform
from flask import Flask
from flask import request
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from data import Data
from elements import barchart, power_gauge, buttongroup, voltagebar, currentbar, energydisplay, datepicker, button, powergraph
from credintials import title, db_table

data = Data(db_table=db_table)

server = Flask(__name__)
app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP], title=title, update_title=None)#, suppress_callback_exceptions=True)
app.scripts.append_script({"external_url": "https://cdn.plot.ly/plotly-locale-cs-latest.js"})
app.css.config.serve_locally = False
app.scripts.config.serve_locally = False

if platform.system() == 'Windows':
    LOCALE = 'cs'
else:
    LOCALE = ('cs_CZ', 'UTF-8')
locale.setlocale(category=locale.LC_ALL, locale=LOCALE)

@server.route('/data', methods = ['POST', 'GET'])
def hello_world():
    if request.method == 'POST':
        posted_data = request.get_json()
        data.parse_data(posted_data)
    return 'Hello from Flask!'


app.layout = html.Div(children=[
    # html.H1(children='Hello Dash'),
    # html.Div(children=''' Dash: A web application framework for your data.'''),
    html.Div(children=[
        power_gauge("power_gauge"),
        voltagebar("voltagebar"),
        currentbar("currentbar"),
        energydisplay("energydisplay")
        ], style={"display": "flex", "justify-content": "center"}
        ),

    html.Div(children=[
        buttongroup("radios"),
        dcc.Graph(id='energygraph', style={"width": "100vw"}, config={"locale": "cs", 'displayModeBar': False}),
        ], style={"display": "flex", "flex-direction": "column", "align-items": "center"}
        ),

    html.Div(children=[
        html.Div(children=[datepicker("datepicker"), button("button")]),
        dcc.Graph(id='powerchart', style={"width": "100vw"}, config={"locale": "cs", 'displayModeBar': False}),
        ], style={"display": "flex", "flex-direction": "column", "align-items": "center"}
        ),
    html.Div(id="testdiv"),

    dcc.Interval(
                id='interval-component',
                interval=5000, # in milliseconds
                n_intervals=0
                )

], style={"display": "flex", "flex-direction": "column"})



@callback([Output('power_gauge', 'value'),
           Output('voltagebar', 'value'),
           Output('currentbar', 'value'),
           Output('energydisplay', 'value')],
          Input('interval-component', 'n_intervals'))
def update_metrics(n):
    return data.power, int(data.voltage), round(data.current, 1), f"{data.energy:.3f}"

@callback(Output('energygraph', 'figure'),
          [Input('radios', 'value')])
def update_barchart(val):
    if val == 1:
        df = data.df_energy_daily
    elif val == 2:
        df = data.df_energy_weekly
    elif val == 3:
        df = data.df_energy_monthly
    fig = barchart(df)
    return fig

@callback(Output('powerchart', 'figure'),
          Input('button', 'n_clicks'),
          State('datepicker', 'start_date'),
          State('datepicker', 'end_date'))
def update_powerchart(n, start_date, end_date):
    start_date += "T05:00:00"
    end_date += "T22:00:00"

    df = data.get_power(start_date, end_date)
    fig = powergraph(df)
    return fig

# if __name__ == '__main__':
#     app.run(debug=True)
