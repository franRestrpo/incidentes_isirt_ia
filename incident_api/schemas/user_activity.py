"""
Pydantic schemas for the User Activity and Cross-Reference feature.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

from . import IncidentInDB # Importar el schema de Incidentes

# --- Individual Activity Schemas ---

class ActivityLogItem(BaseModel):
    """
    Represents a single item in the user's activity timeline (from IncidentLog).
    """
    log_id: int
    incident_id: int
    action: str
    comments: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class HistoryLogItem(BaseModel):
    """
    Represents a single change in the user's history (from IncidentHistory).
    """
    history_id: int = Field(..., alias='id')
    incident_id: int
    field_changed: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

# --- Metrics Schema ---

class UserActivityMetrics(BaseModel):
    """
    Defines the calculated metrics and basic info for a user's activity.
    """
    # User Info
    user_id: int
    full_name: str
    email: str
    role: str
    is_active: bool

    # Calculated Metrics
    total_incidents_created: int
    total_incidents_resolved: int
    total_incidents_assigned: int
    last_login: Optional[datetime] = None
    top_incident_types: List[str]
    average_resolution_time_hours: Optional[float] = None
    incidents_by_status: Dict[str, int]
    login_frequency_per_week: Optional[float] = None
    total_comments_made: int
    total_files_uploaded: int

# --- Main Response Schema ---

class IncidentRelationship(IncidentInDB):
    """Extends IncidentInDB to include the relationship type for the graph."""
    relationship_type: str

class UserCrossReferenceResponse(BaseModel):
    """
    The main response model for the GET /users/{user_id}/cross-reference endpoint.
    It consolidates all cross-referenced information for a user.
    """
    metrics: UserActivityMetrics
    incidents: List[IncidentRelationship]
    activity_logs: List[ActivityLogItem]
    history_logs: List[HistoryLogItem]
