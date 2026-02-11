"""
API endpoints for auditing purposes.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from incident_api.api import dependencies
from incident_api.services import user_activity_service
from incident_api.schemas.user_activity import UserCrossReferenceResponse
from incident_api.models.user import User
from incident_api.services.audit_service import AuditService
from incident_api.services.rate_limiting_service import check_audit_rate_limit
from incident_api.api.decorators import audit_action
from incident_api.services.alerting_service import alerting_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get(
    "/users/{user_id}/cross-reference",
    response_model=UserCrossReferenceResponse,
    summary="Get Cross-Referenced User Activity",
    dependencies=[Depends(dependencies.get_current_audit_user), Depends(check_audit_rate_limit)],
)
@audit_action(action="AUDIT_USER_ACTIVITY", resource_type="user", resource_id_param="user_id")
def get_user_activity(
    user_id: int,
    request: Request,
    activity_log_limit: int = 100,
    history_log_limit: int = 100,
    start_date: Optional[datetime] = Query(None, description="Start date for filtering logs"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering logs"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    incident_status: Optional[str] = Query(None, description="Filter by incident status"),
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_audit_user),
    audit_service: AuditService = Depends(dependencies.get_audit_service),
):
    """
    Retrieve a consolidated report of all activities for a specific user.

    This endpoint is protected and only accessible by users with the 'ADMINISTRADOR' or 'SUPER_ADMIN' role.
    Admins and Super Admins can audit their own activity, but it will be logged as a warning.
    """
    # Log a warning and trigger a critical alert if an administrator is auditing their own activity.
    if user_id == current_user.user_id:
        alert_message = f"SECURITY_ALERT: Self-audit performed by user '{current_user.email}' (ID: {current_user.user_id})."
        logger.warning(alert_message)
        alerting_service.trigger_alert(alert_message, level="critical")

    try:
        return user_activity_service.get_cross_reference_for_user(
            db=db, user_id=user_id, activity_log_limit=activity_log_limit, history_log_limit=history_log_limit,
            start_date=start_date, end_date=end_date, activity_type=activity_type, incident_status=incident_status
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
