"""
Modelos de la base de datos para historiales.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from incident_api.db.base import Base


class IncidentHistory(Base):
    """
    Modelo para registrar los cambios en los incidentes para trazabilidad.
    """

    __tablename__ = "incident_history"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("Incidents.incident_id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(
        Integer, ForeignKey("Users.user_id"), nullable=True
    )  # Quién hizo el cambio (puede ser sistema)
    field_changed = Column(String, nullable=False)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    details = Column(String, nullable=True)  # Detalles adicionales del cambio

    incident = relationship("Incident", back_populates="history")
    user = relationship("User", back_populates="incident_history")


class ConversationHistory(Base):
    """
    Modelo para almacenar el historial de conversaciones del chatbot.
    """

    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(
        String, index=True, nullable=False
    )  # ID para agrupar mensajes de una misma conversación
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    role = Column(String, nullable=False)  # 'user' o 'assistant'
    message_content = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="conversation_history")
