import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.connectors.base import ConnectorHealth


class MockGujaratPortalConnector:
    """Connector for Digital Gujarat and e-Samaj Kalyan state departmental portals."""

    source_system = "DIGITAL_GUJARAT"

    def __init__(self):
        self._fixture_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "fixtures", "schemes.json"
        )

    def fetch_schemes(self) -> List[Dict[str, Any]]:
        """Fetch Gujarat State schemes from master fixture."""
        if not os.path.exists(self._fixture_path):
            return []

        with open(self._fixture_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [s for s in data.get("schemes", []) if s.get("level") == "STATE"]

    def fetch_application_status(
        self, applicant_token: str, external_ref: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Simulate fetching application status from Gujarat portal."""
        return [
          {
            "external_ref": external_ref or "GJ-REF-8899",
            "status": "UNDER_REVIEW",
            "status_updated_at": datetime.utcnow().isoformat(),
            "source_system": self.source_system,
          }
        ]

    def health(self) -> ConnectorHealth:
        return ConnectorHealth(
            source_system=self.source_system,
            status="HEALTHY",
            last_checked_at=datetime.utcnow().isoformat(),
            latency_ms=18.5,
        )


mock_gujarat_connector = MockGujaratPortalConnector()
