"""
Servicio para el registro de auditoría de acciones de usuarios.

Este módulo proporciona funcionalidades para registrar y consultar
acciones de usuarios para trazabilidad y auditorías.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Request
from datetime import datetime, timezone

from incident_api import crud, models


class AuditService:
    """
    Servicio para gestionar el registro de auditoría de acciones de usuarios.
    """

    def log_action(
        self,
        db: Session,
        action: str,
        resource_type: str,
        user_id: Optional[int] = None,
        resource_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
        success: bool = True,
    ) -> models.AuditLog:
        """
        Registra una acción de usuario en el log de auditoría.

        Args:
            db: Sesión de base de datos
            action: Tipo de acción (e.g., 'LOGIN', 'CREATE_INCIDENT')
            resource_type: Tipo de recurso afectado (e.g., 'USER', 'INCIDENT')
            user_id: ID del usuario que realizó la acción (opcional).
            resource_id: ID del recurso específico (opcional)
            details: Detalles adicionales en formato JSON (opcional)
            request: Objeto Request de FastAPI para extraer IP y user agent (opcional)
            success: Indica si la acción fue exitosa

        Returns:
            El registro de auditoría creado
        """
        # Extraer información de la request si está disponible
        ip_address = None
        user_agent = None

        if request:
            ip_address = self._get_client_ip(request)
            user_agent = request.headers.get("user-agent")

        # Crear el registro de auditoría
        audit_data = {
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "success": success,
        }

        return crud.audit_log.create(db, obj_in=audit_data)

    def get_user_audit_logs(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[models.AuditLog]:
        """
        Obtiene los registros de auditoría de un usuario con filtros opcionales.

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            action: Filtrar por tipo de acción
            resource_type: Filtrar por tipo de recurso
            start_date: Fecha de inicio del filtro
            end_date: Fecha de fin del filtro

        Returns:
            Lista de registros de auditoría
        """
        query = db.query(models.AuditLog).filter(models.AuditLog.user_id == user_id)

        if action:
            query = query.filter(models.AuditLog.action == action)

        if resource_type:
            query = query.filter(models.AuditLog.resource_type == resource_type)

        if start_date:
            query = query.filter(models.AuditLog.timestamp >= start_date)

        if end_date:
            query = query.filter(models.AuditLog.timestamp <= end_date)

        return query.order_by(models.AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

    def get_paged_audit_logs(
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
    ) -> tuple[list[models.AuditLog], int]:
        """
        Obtiene una lista paginada de logs de auditoría con filtros avanzados.

        Args:
            db: Sesión de base de datos.
            user_id: Filtrar por ID de usuario.
            action: Filtrar por tipo de acción.
            resource_type: Filtrar por tipo de recurso.
            start_date: Fecha de inicio del filtro.
            end_date: Fecha de fin del filtro.
            skip: Número de registros a omitir.
            limit: Número máximo de registros a devolver.

        Returns:
            Una tupla conteniendo la lista de logs y el conteo total.
        """
        return crud.audit_log.get_multi_with_filters(
            db=db,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit,
        )

    def _get_client_ip(self, request: Request) -> str:
        """
        Extrae la dirección IP del cliente de la request.

        Args:
            request: Objeto Request de FastAPI

        Returns:
            Dirección IP del cliente
        """
        # Verificar headers comunes para IP
        ip_headers = [
            "x-forwarded-for",
            "x-real-ip",
            "x-client-ip",
            "cf-connecting-ip",
            "fastly-client-ip",
        ]

        for header in ip_headers:
            ip = request.headers.get(header)
            if ip:
                # x-forwarded-for puede contener múltiples IPs separadas por coma
                return ip.split(",")[0].strip()

        # Fallback a la IP del cliente directo
        return request.client.host if request.client else "unknown"


audit_service = AuditService()