import requests
import streamlit as st
import logging
from typing import Dict, Any, Optional
from config import API_URL

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            response = requests.get(f"{self.base_url}/{endpoint}", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API Error ({endpoint}): {str(e)}")
            logger.error(f"API request failed: {str(e)}")
            return {}

    def get_health(self) -> Dict[str, Any]:
        return self._get("health/")

    def get_health_score(self) -> Dict[str, Any]:
        return self._get("health/score")

    def get_logs(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._get("logs/", params=params)

    def get_log_summary(self) -> Dict[str, Any]:
        return self._get("logs/statistics/summary")

    def get_anomalies(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._get("anomalies/", params=params)

    def get_anomaly_summary(self) -> Dict[str, Any]:
        return self._get("anomalies/statistics/summary")

    def get_alerts(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._get("alerts/", params=params)

    def get_alert_summary(self) -> Dict[str, Any]:
        return self._get("alerts/statistics/summary")

api_client = APIClient()
