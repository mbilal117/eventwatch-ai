import streamlit as st
from config import APP_TITLE, APP_ICON, LAYOUT, INITIAL_SIDEBAR_STATE

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE
)

def main():
    st.title(f"{APP_ICON} {APP_TITLE}")

    st.markdown("""
    ### Welcome to EventWatch AI
    
    Your intelligent log monitoring and anomaly detection system.
    
    #### Quick Navigation:
    - **Overview**: High-level system health and summary metrics.
    - **Log Explorer**: Deep dive into your system logs with filtering and search.
    - **Anomaly Analysis**: Identify and analyze unusual patterns in your logs.
    - **Alert Center**: Manage and track critical system alerts.
    
    ---
    *Use the sidebar to navigate between different views.*
    """)

    with st.expander("System Information", expanded=False):
        st.info("""
        - **Backend URL**: http://localhost:8001
        - **Documentation**: [Swagger UI](http://localhost:8001/docs)
        - **Status**: Connected
        """)

if __name__ == "__main__":
    main()
