from datetime import date, timedelta
from dash import dcc
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objs as go
from credintials import max_power, max_voltage, max_current


def power_gauge(id):
    gauge = daq.Gauge(
                    id=id,
                    showCurrentValue=True,
                    color="orange",
                    units="W",
                    value=0,
                    label='Výkon [W]',
                    max=max_power,
                    min=0
                    )
    return gauge

def voltagebar(id):
    bar = daq.Tank(
        id=id,
        color="#EC7063",
        scale={'custom': {'0': ''}},
        label={"label": 'Napětí',
               "style": {"font-weight": "bold",
                         "margin-bottom": -22,
                         "font-size": 10,
                         "z-index": "3",
                         "color": "#000058"
                         }
                },
        width=70,
        min=0,
        max=max_voltage,
        units='V',
        style={'margin-top': '50px', 'margin-left': '30px'},
        # style={"position": "absolute", "top": 1000, "left": 1000},
        showCurrentValue=True
            )
    return bar

def currentbar(id):
    bar = daq.Tank(
        id=id,
        color="#85C1E9",
        scale={'custom': {'0': ''}},
        label={"label": 'Proud',
               "style": {"font-weight": "bold",
                         "margin-bottom": -22,
                         "font-size": 10,
                         "z-index": "3",
                         "color": "#000058"
                         }
                },
        width=70,
        min=0,
        max=max_current,
        units='A',
        style={'margin-top': '50px', 'margin-left': '30px'},
        # style={"position": "absolute", "top": 1000, "left": 1000},
        showCurrentValue=True
            )
    return bar

def energydisplay(id):
    led = daq.LEDDisplay(
                id=id,
                label="Výroba TOTAL [kWh]",
                size=64,
                color="#273746",
                style={'margin-top': '50px', 'margin-left': '30px'},
                    )
    return led

def buttongroup(id):
    button_group = dbc.RadioItems(
                        id=id,
                        className="btn-group",
                        inputClassName="btn-check",
                        labelClassName="btn btn-outline-primary",
                        labelCheckedClassName="active",
                        options=[
                            {"label": "Dny", "value": 1},
                            {"label": "Týdny", "value": 2},
                            {"label": "Měsíce", "value": 3},
                            ],
                        value=1,
                        )
    return button_group

def barchart(df):
    y_column = df.columns[1]
    fig = px.bar(df, x="time", y=y_column, text_auto='.2s')#, color="City", barmode="group")
    fig.update_yaxes(fixedrange=True)
    fig.update_layout(xaxis_title=None, margin=dict(l=50, r=20, t=20, b=50))
    # fig.update_xaxes(tickangle=45)
    return fig

def datepicker(id):
    picker = dcc.DatePickerRange(
                id=id,
                display_format="D.M.YYYY",
                start_date=date.today()-timedelta(days=1),
                end_date=date.today()
                )
    return picker

def button(id):
    button = dbc.Button("OK", id=id, color="primary", className="me-1")
    return button

def powergraph(df):
    orange = 'rgb(237, 159, 43)'
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=df["VÝKON"], name="VÝKON [W]", line_shape='spline', fill='tozeroy', line=dict(color=orange)))
    fig.update_layout(xaxis=dict(domain=[0.02, 0.977], showgrid=False),
                      yaxis=dict(titlefont=dict(color=orange), range=[0, max_power], title="VÝKON [W]"),
                      margin=dict(l=50, r=20, t=20, b=50))
    fig.update_yaxes(fixedrange=True)
    return fig