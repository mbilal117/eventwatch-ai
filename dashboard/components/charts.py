import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any

def render_severity_distribution(data: List[Dict[str, Any]]):
    if not data:
        return None

    df = pd.DataFrame(data)
    fig = px.pie(df, values='count', names='level', title='Severity Distribution',
                 color='level', color_discrete_map={
                     'ERROR': '#ef553b',
                     'WARNING': '#fec032',
                     'INFO': '#636efa',
                     'DEBUG': '#00cc96'
                 })
    return fig

def render_trend_chart(data: List[Dict[str, Any]], title: str, x: str, y: str, color: str = None):
    if not data:
        return None

    df = pd.DataFrame(data)
    fig = px.line(df, x=x, y=y, color=color, title=title, markers=True)
    fig.update_layout(xaxis_title="Time", yaxis_title="Count")
    return fig

def render_alert_timeline(alerts: List[Dict[str, Any]]):
    if not alerts:
        return None

    df = pd.DataFrame(alerts)
    if df.empty:
        return None

    # Simplify for timeline
    timestamp_field = None

    if 'triggered_at' in df.columns:
        timestamp_field = 'triggered_at'
    elif 'created_at' in df.columns:
        timestamp_field = 'created_at'

    if not timestamp_field:
        return None

    df['timestamp'] = pd.to_datetime(df[timestamp_field])
    fig = px.scatter(df, x='timestamp', y='severity', color='alert_type',
                     hover_data=[
                         'message',
                         'severity',
                         'triggered_at'
                     ],
                     title='Alert Timeline')
    return fig
