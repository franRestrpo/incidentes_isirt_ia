"""
Business logic for user activity and cross-referencing.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from incident_api.crud import (
    crud_user,
    crud_incident,
    crud_audit_log,
    crud_incident_log,
    crud_history,
    crud_evidence_file,
)
from incident_api.schemas.user_activity import UserCrossReferenceResponse, UserActivityMetrics, IncidentRelationship
from incident_api.schemas.incident import IncidentInDB

def get_cross_reference_for_user(db: Session, user_id: int, activity_log_limit: int = 100, history_log_limit: int = 100, start_date: datetime | None = None, end_date: datetime | None = None, activity_type: str | None = None, incident_status: str | None = None) -> UserCrossReferenceResponse:
    """
    Gathers all cross-referenced activity for a specific user.
    """
    user = crud_user.user.get(db, id=user_id)
    if not user:
        raise ValueError("User not found")

    # 1. Fetch all raw data
    total_created = crud_incident.incident.count_by_reporter(db, user_id=user_id)
    total_resolved = crud_incident.incident.count_resolved_by_assignee(db, user_id=user_id)
    total_assigned = crud_incident.incident.count_assigned_to_user(db, user_id=user_id)
    last_login_log = crud_audit_log.audit_log.get_last_login_by_user(db, user_id=user_id)
    top_incident_types = crud_incident.incident.get_top_incident_types_by_user(db, user_id=user_id)
    avg_resolution_time = crud_incident.incident.get_average_resolution_time_by_assignee(db, user_id=user_id)
    incidents_by_status_counts = crud_incident.incident.get_incidents_by_status_for_user(db, user_id=user_id)
    login_frequency = crud_audit_log.audit_log.get_login_frequency_per_week(db, user_id=user_id)
    total_comments = crud_incident_log.incident_log.count_comments_by_user(db, user_id=user_id)
    total_files = crud_evidence_file.evidence_file.count_by_uploader(db, user_id=user_id)
    
    associated_incidents = crud_incident.incident.get_multi_by_user_association(db, user_id=user_id)

    activity_logs = crud_incident_log.incident_log.get_by_user(db, user_id=user_id, limit=activity_log_limit)
    history_logs = crud_history.incident_history.get_by_user(db, user_id=user_id, limit=history_log_limit)

    # 2. Assemble the metrics object
    metrics = UserActivityMetrics(
        user_id=user.user_id,
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        total_incidents_created=total_created,
        total_incidents_resolved=total_resolved,
        total_incidents_assigned=total_assigned,
        last_login=last_login_log.timestamp if last_login_log else None,
        top_incident_types=[str(t) for t in top_incident_types],
        average_resolution_time_hours=avg_resolution_time,
        incidents_by_status=incidents_by_status_counts,
        login_frequency_per_week=login_frequency,
        total_comments_made=total_comments,
        total_files_uploaded=total_files,
    )

    # 3. Assemble the incidents list with relationship type
    incidents_with_relationship = []
    for incident in associated_incidents:
        relationship = "reportado" if incident.reported_by_id == user_id else "asignado"
        incident_model = IncidentInDB.model_validate(incident)
        incident_rel = IncidentRelationship(**incident_model.model_dump(), relationship_type=relationship)
        incidents_with_relationship.append(incident_rel)

    # 4. Assemble the final response object
    response = UserCrossReferenceResponse(
        metrics=metrics,
        incidents=incidents_with_relationship,
        activity_logs=activity_logs,
        history_logs=history_logs,
    )

    return response
