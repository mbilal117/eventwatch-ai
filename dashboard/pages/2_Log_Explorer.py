import streamlit as st
import pandas as pd
from components.api_client import api_client

st.set_page_config(page_title="Log Explorer - EventWatch AI", layout="wide")

st.title("🔍 Log Explorer")

# Sidebar filters
st.sidebar.header("Filters")
search_term = st.sidebar.text_input("Search message")
level = st.sidebar.selectbox("Severity Level", ["All", "DEBUG", "INFO", "WARNING", "ERROR"])
page_size = st.sidebar.slider("Logs per page", 10, 500, 50)
page = st.sidebar.number_input("Page", min_value=1, value=1)

params = {
    "page": page,
    "page_size": page_size
}
if search_term:
    params["search_term"] = search_term
if level != "All":
    params["level"] = level

# Fetch data
with st.spinner("Fetching logs..."):
    log_data = api_client.get_logs(params)

if log_data:
    total = log_data.get("total", 0)
    st.write(f"Showing {len(log_data.get('logs', []))} of {total} logs")

    if log_data.get("logs"):
        df = pd.DataFrame(log_data.get("logs"))
        # Clean up dataframe for display
        display_cols = ['timestamp', 'level', 'service', 'message', 'source']
        existing_cols = [c for c in display_cols if c in df.columns]

        st.dataframe(df[existing_cols], use_container_width=True, hide_index=True)

        # Pagination info
        st.write(f"Page {log_data.get('page')} of {log_data.get('pages')}")
    else:
        st.info("No logs found matching the filters.")
else:
    st.error("Failed to fetch logs.")
