import os

# Backend API Configuration
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8001")
API_PREFIX = "/api"
API_URL = f"{BACKEND_BASE_URL}{API_PREFIX}"

# Dashboard Settings
APP_TITLE = "EventWatch AI Dashboard"
APP_ICON = "🛡️"

# Refresh intervals (in seconds)
DEFAULT_REFRESH_INTERVAL = 60

# Page Config
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"
