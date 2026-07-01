import streamlit as st
import pandas as pd
import plotly.express as px
from components.api_client import api_client

st.set_page_config(page_title="Anomaly Analysis - EventWatch AI", layout="wide")

st.title("🧠 Anomaly Analysis")

# Fetch stats
with st.spinner("Loading anomaly stats..."):
    stats = api_client.get_anomaly_summary()

if stats:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Anomalies", stats.get("total_anomalies", 0))
    col2.metric("Anomaly %", f"{stats.get('anomaly_percentage', 0):.2f}%")
    col3.metric("Avg Score", f"{stats.get('average_score', 0):.2f}")
    col4.metric("Max Score", f"{stats.get('max_score', 0):.2f}")

st.divider()

# Sidebar filters
st.sidebar.header("Filters")
min_score = st.sidebar.slider("Min Anomaly Score", 0.0, 1.0, 0.0)
algorithm = st.sidebar.selectbox("Algorithm", ["All", "isolation_forest", "statistical", "spike", "pattern"])

params = {"min_score": min_score}
if algorithm != "All":
    params["algorithm"] = algorithm

# Fetch anomalies
with st.spinner("Fetching anomalies..."):
    anomaly_data = api_client.get_anomalies(params)

if anomaly_data:
    anomalies = anomaly_data.get("anomalies", [])
    if anomalies:
        df = pd.DataFrame(anomalies)

        col1, col2 = st.columns(2)

        with col1:
            # Severity (Score) breakdown
            fig_score = px.histogram(
                df,
                x="anomaly_score",
                nbins=20,
                title="Anomaly Score Distribution"
            )
            st.plotly_chart(fig_score, use_container_width=True)

        with col2:
            # Detection method breakdown
            fig_algo = px.pie(df, names="algorithm", title="Detection Method Breakdown")
            st.plotly_chart(fig_algo, use_container_width=True)

        st.subheader("Detected Anomalies")
        # Format for table
        display_df = pd.DataFrame([
            {
                "ID": a["id"],
                "Score": f"{a['anomaly_score']:.4f}",
                "Algorithm": a["algorithm"],
                "Log Message": a.get("log_entry", {}).get("message", "N/A"),
                "Timestamp": a.get("log_entry", {}).get("timestamp", "N/A")
            } for a in anomalies
        ])
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No anomalies found with current filters.")
else:
    st.error("Failed to fetch anomaly data.")
