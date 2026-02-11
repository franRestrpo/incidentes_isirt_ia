"""
Modelo de la base de datos para los Grupos de Trabajo.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from incident_api.db.base import Base


class Group(Base):
    """
    Modelo ORM para la tabla `groups`.

    Representa un grupo de usuarios, como un equipo de respuesta a incidentes.

    Atributos:
        id (int): Identificador único del grupo.
        name (str): Nombre único del grupo.
        description (str, opcional): Descripción del propósito del grupo.

    Relaciones:
        users: Lista de usuarios que pertenecen a este grupo.
    """

    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)

    users = relationship("User", back_populates="group")
