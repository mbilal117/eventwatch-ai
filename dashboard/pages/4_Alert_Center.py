import streamlit as st
import pandas as pd
from components.api_client import api_client

st.set_page_config(page_title="Alert Center - EventWatch AI", layout="wide")

st.title("🚨 Alert Center")

# Fetch stats
with st.spinner("Loading alert stats..."):
    stats = api_client.get_alert_summary()

if stats:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Alerts", stats.get("total_alerts", 0))
    col2.metric("Active Alerts", stats.get("active_alerts", 0), delta_color="inverse")
    col3.metric("Resolved Alerts", stats.get("resolved_alerts", 0))
    col4.metric("Avg Resolution Time", f"{stats.get('average_resolution_time_hours', 0):.1f}h")

st.divider()

# Sidebar filters
st.sidebar.header("Filters")
severity = st.sidebar.selectbox("Severity", ["All", "LOW", "MEDIUM", "HIGH", "CRITICAL"])
status = st.sidebar.selectbox("Status", ["All", "active", "resolved", "escalated"])

params = {}
if severity != "All":
    params["severity"] = severity
if status != "All":
    params["status"] = status

# Fetch alerts
with st.spinner("Fetching alerts..."):
    alert_data = api_client.get_alerts(params)

if alert_data:
    alerts = alert_data.get("alerts", [])
    if alerts:
        # Display as a list of expandable items for detail
        for alert in alerts:
            severity_color = {
                "CRITICAL": "🔴",
                "HIGH": "🟠",
                "MEDIUM": "🟡",
                "LOW": "🔵"
            }.get(alert['severity'], "⚪")

            with st.expander(f"{severity_color} {alert['severity']} - {alert['alert_type']}: {alert['message'][:100]}..."):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**Severity:** {alert['severity']}")
                    st.write(f"**Created At:** {alert['triggered_at']}")
                    st.write(f"**Alert Type:** {alert['alert_type']}")
                with col_b:
                    st.write(f"**Message:** {alert['message']}")
                    if alert.get('resolved_at'):
                        st.write(f"**Resolved At:** {alert['resolved_at']}")

                st.json(alert.get("metadata") or {})

                # Action buttons (simplified - just placeholders in this version)
                if alert['severity'] != "resolved":
                    if st.button("Mark as Resolved", key=f"res_{alert['id']}"):
                        st.info(f"Resolution functionality would call PUT /api/alerts/{alert['id']}/resolve")
    else:
        st.info("No alerts found matching the filters.")
else:
    st.error("Failed to fetch alerts.")
