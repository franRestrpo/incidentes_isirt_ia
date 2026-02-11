"""
Modelo de la base de datos para las tareas en segundo plano.
"""

from sqlalchemy import Column, Integer, String, JSON
from incident_api.db.base import Base


class Task(Base):
    """
    Modelo ORM para la tabla `Tasks`.
    """

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, nullable=False)
    result = Column(JSON)
