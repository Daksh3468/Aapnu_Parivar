from typing import Dict, List, Any
from app.connectors.base import SourceConnector, ConnectorHealth
from app.connectors.mock_central_portal import mock_central_connector
from app.connectors.mock_gujarat_portal import mock_gujarat_connector
from app.connectors.mock_uidai import mock_uidai


class ConnectorRegistry:
    """Central registry managing departmental connectors."""

    def __init__(self):
        self._connectors: Dict[str, Any] = {
            "CENTRAL_PORTAL": mock_central_connector,
            "DIGITAL_GUJARAT": mock_gujarat_connector,
            "UIDAI_EKYC": mock_uidai,
        }

    def get_connector(self, source_system: str) -> Any:
        connector = self._connectors.get(source_system)
        if connector:
            return connector
        # The catalog preserves portal-specific source labels (for example PMKISAN_PORTAL).
        # Until a dedicated adapter is added, central portal labels use the central mock adapter.
        if source_system and source_system.endswith("_PORTAL"):
            return mock_central_connector
        return None

    def get_all_scheme_connectors(self) -> List[Any]:
        return [mock_central_connector, mock_gujarat_connector]

    def get_health_all(self) -> List[ConnectorHealth]:
        healths = []
        for name, conn in self._connectors.items():
            if hasattr(conn, "health"):
                healths.append(conn.health())
        return healths


connector_registry = ConnectorRegistry()
