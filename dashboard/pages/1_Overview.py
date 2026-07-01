import streamlit as st
import pandas as pd
from components.api_client import api_client
from components.metrics import render_health_metric, render_summary_metrics
from components.charts import render_severity_distribution, render_trend_chart, render_alert_timeline

st.set_page_config(page_title="Overview - EventWatch AI", layout="wide")

st.title("📊 System Overview")

# Fetch data
with st.spinner("Loading metrics..."):
    health_data = api_client.get_health_score()
    log_summary = api_client.get_log_summary()
    alert_summary = api_client.get_alert_summary()
    alerts = api_client.get_alerts({"page_size": 100})

if health_data and health_data.get("success"):
    render_health_metric(health_data.get("health_score", 0), health_data.get("status", "unknown"))
    st.divider()
    render_summary_metrics(health_data.get("details", {}))
else:
    st.error("Could not fetch health data. Is the backend running?")

st.divider()

col1, col2 = st.columns(2)

with col1:
    if log_summary and log_summary.get("success"):
        stats = log_summary.get("data", {})
        severity_data = []
        for level, count in stats.get("logs_by_level", {}).items():
            severity_data.append({"level": level, "count": count})

        fig = render_severity_distribution(severity_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No log data available for distribution chart.")

with col2:
    if alerts and alerts.get("alerts"):
        fig = render_alert_timeline(alerts.get("alerts"))
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No alert data available for timeline.")
    else:
        st.info("No active alerts.")

st.subheader("Recent Alerts")
if alerts and alerts.get("alerts"):
    df_alerts = pd.DataFrame(alerts.get("alerts"))
    st.table(df_alerts[['triggered_at', 'severity', 'alert_type', 'message', 'webhook_sent']].head(5))
else:
    st.write("No recent alerts found.")
