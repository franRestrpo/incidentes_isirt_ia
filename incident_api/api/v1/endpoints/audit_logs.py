"""
API endpoints for querying audit logs.
"""
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from incident_api import models, schemas
from incident_api.api import dependencies
from incident_api.services.audit_service import AuditService

logger = logging.getLogger(__name__)
router = APIRouter()


class AuditLogResponse(BaseModel):
    """Response model for paginated audit logs."""
    total: int
    logs: List[schemas.AuditLogInDB]


@router.get(
    "/",
    response_model=AuditLogResponse,
    summary="Query Audit Logs",
    dependencies=[Depends(dependencies.get_current_admin_user)],
)
def read_audit_logs(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin_user),
    user_id: Optional[int] = Query(None, description="Filter by user ID."),
    action: Optional[str] = Query(None, description="Filter by action name (case-insensitive search)."),
    resource_type: Optional[str] = Query(None, description="Filter by resource type (case-insensitive search)."),
    start_date: Optional[datetime] = Query(None, description="Filter logs from this date onwards."),
    end_date: Optional[datetime] = Query(None, description="Filter logs up to this date."),
    skip: int = Query(0, ge=0, description="Pagination skip."),
    limit: int = Query(100, ge=1, le=500, description="Pagination limit."),
):
    """
    Retrieve a paginated and filterable list of audit logs.

    Requires **Administrator** privileges.
    """
    audit_service = AuditService()
    logs, total = audit_service.get_paged_audit_logs(
        db=db,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )
    return {"total": total, "logs": logs}
