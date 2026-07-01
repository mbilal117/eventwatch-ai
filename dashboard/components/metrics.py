import streamlit as st
from typing import Dict, Any

def render_health_metric(health_score: float, status: str):
    color = "normal"
    if status == "critical":
        color = "inverse"
    elif status == "warning":
        color = "off"

    st.metric(
        label="System Health Score",
        value=f"{health_score}%",
        delta=status.upper(),
        delta_color=color
    )

def render_summary_metrics(metrics: Dict[str, Any]):
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Logs", metrics.get("total_logs", 0))
    with col2:
        st.metric("Errors", metrics.get("error_count", 0), delta=None, delta_color="inverse")
    with col3:
        st.metric("Warnings", metrics.get("warning_count", 0), delta=None, delta_color="off")
    with col4:
        st.metric("Anomalies", metrics.get("anomaly_count", 0), delta=None, delta_color="inverse")
    with col5:
        st.metric("Active Alerts", metrics.get("active_alerts", 0), delta=None, delta_color="inverse")
