import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.connectors.base import ConnectorHealth


class MockCentralPortalConnector:
    """Connector for Central Government scheme portals (PM-KISAN, PM-JAY, PMAY)."""

    source_system = "CENTRAL_PORTAL"

    def __init__(self):
        self._fixture_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "fixtures", "schemes.json"
        )

    def fetch_schemes(self) -> List[Dict[str, Any]]:
        """Fetch central government schemes from master fixture."""
        if not os.path.exists(self._fixture_path):
            return []

        with open(self._fixture_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [s for s in data.get("schemes", []) if s.get("level") == "CENTRAL"]

    def fetch_application_status(
        self, applicant_token: str, external_ref: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Simulate fetching application status from Central portal."""
        return [
          {
            "external_ref": external_ref or "CENTRAL-REF-1001",
            "status": "APPROVED",
            "status_updated_at": datetime.utcnow().isoformat(),
            "source_system": self.source_system,
          }
        ]

    def health(self) -> ConnectorHealth:
        return ConnectorHealth(
            source_system=self.source_system,
            status="HEALTHY",
            last_checked_at=datetime.utcnow().isoformat(),
            latency_ms=45.2,
        )


mock_central_connector = MockCentralPortalConnector()
