"""
Modelo de la base de datos para la Bitácora de Incidentes.

Este módulo define el modelo `IncidentLog`, que representa la tabla `IncidentLog`.
Funciona como una bitácora de auditoría para cada incidente, registrando todas
las acciones y cambios significativos.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from incident_api.db.base import Base


class IncidentLog(Base):
    """
    Modelo ORM para la tabla `IncidentLog`.

    Registra un historial de eventos para cada incidente, como cambios de estado,
    asignaciones, y comentarios, proporcionando una línea de tiempo clara de las acciones tomadas.

    Atributos:
        log_id (int): Identificador único de la entrada de la bitácora.
        incident_id (int): ID del incidente al que se refiere esta entrada.
        user_id (int): ID del usuario que realizó la acción.
        action (str): Tipo de acción realizada (e.g., 'Creación', 'Cambio de estado').
        field_modified (str, opcional): El campo del incidente que fue modificado.
        old_value (str, opcional): El valor del campo antes del cambio.
        new_value (str, opcional): El valor del campo después del cambio.
        comments (str, opcional): Comentarios adicionales del usuario.
        timestamp (datetime): Fecha y hora en que se registró la acción.

    Relaciones:
        incident: Relación con el incidente al que pertenece la bitácora.
        user: Relación con el usuario que generó la entrada.
    """

    __tablename__ = "IncidentLog"

    log_id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Identificador único de la entrada de log.",
    )
    incident_id = Column(
        Integer,
        ForeignKey("Incidents.incident_id"),
        nullable=False,
        doc="ID del incidente asociado.",
    )
    user_id = Column(
        Integer,
        ForeignKey("Users.user_id"),
        nullable=False,
        doc="ID del usuario que realizó la acción.",
    )

    action = Column(
        String(50),
        nullable=False,
        doc="Acción realizada (e.g., 'Creación', 'Actualización').",
    )
    field_modified = Column(
        String(100), nullable=True, doc="Campo que fue modificado en el incidente."
    )
    old_value = Column(Text, nullable=True, doc="Valor antiguo del campo modificado.")
    new_value = Column(Text, nullable=True, doc="Valor nuevo del campo modificado.")
    comments = Column(
        Text, nullable=True, doc="Comentarios adicionales sobre la acción."
    )
    timestamp = Column(
        DateTime,
        server_default=func.now(),
        doc="Fecha y hora del registro de la acción.",
    )

    # Relaciones con las tablas Incident y User
    incident = relationship("Incident", back_populates="logs")
    user = relationship("User", back_populates="logs")
