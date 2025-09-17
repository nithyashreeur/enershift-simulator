# visualization.py
import plotly.graph_objects as go
import pandas as pd

def plot_village_timeseries(df_schedule, title="Energy flows"):
    df = df_schedule.copy()
    x = df['timestamp'] if 'timestamp' in df.columns else list(range(len(df)))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=df['demand'], mode='lines', name='Demand'))
    fig.add_trace(go.Scatter(x=x, y=df['solar'], mode='lines', name='Solar'))
    if 'wind' in df.columns:
        fig.add_trace(go.Scatter(x=x, y=df['wind'], mode='lines', name='Wind'))
    fig.add_trace(go.Scatter(x=x, y=df['battery_soc'], mode='lines', name='Battery SOC', yaxis='y2'))
    fig.update_layout(title=title,
                      xaxis_title='Time',
                      yaxis_title='kW',
                      yaxis2=dict(title='SOC (fraction)', overlaying='y', side='right', range=[0,1]))
    return fig
