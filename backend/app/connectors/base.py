from typing import Protocol, List, Optional, Any, Dict
from pydantic import BaseModel


class ConnectorHealth(BaseModel):
    source_system: str
    status: str  # HEALTHY, DEGRADED, DOWN
    last_checked_at: str
    latency_ms: float


class SourceConnector(Protocol):
    """Protocol interface that every departmental source system connector must implement."""

    source_system: str

    def fetch_schemes(self) -> List[Dict[str, Any]]:
        ...

    def fetch_application_status(
        self, applicant_token: str, external_ref: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        ...

    def health(self) -> ConnectorHealth:
        ...
