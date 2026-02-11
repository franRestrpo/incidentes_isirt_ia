"""
Operaciones CRUD para el modelo AuditLog.
"""

from typing import List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from incident_api.crud.base import CRUDBase
from incident_api.models.audit_log import AuditLog
from incident_api.schemas.audit_log import AuditLogCreate, AuditLogUpdate


class CRUDAuditLog(CRUDBase[AuditLog, AuditLogCreate, AuditLogUpdate]):
    """
    Clase CRUD para el modelo AuditLog.
    """

    def get_multi_by_user(
        self,
        db: Session,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Obtiene múltiples registros de auditoría por usuario."""
        return (
            db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(AuditLog.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_resource(
        self,
        db: Session,
        *,
        resource_type: str,
        resource_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Obtiene múltiples registros de auditoría por recurso."""
        return (
            db.query(AuditLog)
            .filter(
                AuditLog.resource_type == resource_type,
                AuditLog.resource_id == resource_id
            )
            .order_by(AuditLog.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_last_login_by_user(self, db: Session, *, user_id: int) -> AuditLog | None:
        """Gets the last successful login for a user."""
        return (
            db.query(self.model)
            .filter(
                self.model.user_id == user_id,
                self.model.action == "LOGIN_SUCCESS",  # Assuming this is the action name
                self.model.success == True,
            )
            .order_by(self.model.timestamp.desc())
            .first()
        )

    def get_login_frequency_per_week(self, db: Session, *, user_id: int, days: int = 30) -> float | None:
        """Calculates the average logins per week for a user over the last N days."""
        from sqlalchemy import func
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        count = db.query(func.count(self.model.id)).filter(
            self.model.user_id == user_id,
            self.model.action == "LOGIN_SUCCESS",
            self.model.success == True,
            self.model.timestamp >= cutoff
        ).scalar()
        weeks = days / 7.0
        return count / weeks if weeks > 0 else None

    def get_multi_with_filters(
        self,
        db: Session,
        *,
        user_id: int | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[AuditLog], int]:
        """Obtiene múltiples registros de auditoría con filtros dinámicos y paginación."""
        query = db.query(self.model)

        if user_id is not None:
            query = query.filter(self.model.user_id == user_id)
        if action:
            query = query.filter(self.model.action.ilike(f"%{action}%"))
        if resource_type:
            query = query.filter(self.model.resource_type.ilike(f"%{resource_type}%"))
        if start_date:
            query = query.filter(self.model.timestamp >= start_date)
        if end_date:
            query = query.filter(self.model.timestamp <= end_date)

        total = query.count()

        logs = (
            query.order_by(self.model.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return logs, total


audit_log = CRUDAuditLog(AuditLog)