"""
Modelo de la base de datos para los Vectores de Ataque.
"""

from sqlalchemy import Column, Integer, String
from incident_api.db.base import Base


class AttackVector(Base):
    """
    Modelo ORM para la tabla `AttackVectors`.

    Define los vectores de ataque o puntos de entrada a través de los cuales
    puede ocurrir un incidente de seguridad.

    Atributos:
        attack_vector_id (int): ID único del vector de ataque.
        name (str): Nombre del vector (ej: "Correo Electrónico (Phishing)").
        description (str): Descripción del vector de ataque.
    """

    __tablename__ = "AttackVectors"

    attack_vector_id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Identificador único del vector de ataque.",
    )
    name = Column(
        String(255),
        nullable=False,
        unique=True,
        doc="Nombre único del vector de ataque.",
    )
    description = Column(
        String(512), nullable=True, doc="Descripción detallada del vector de ataque."
    )
