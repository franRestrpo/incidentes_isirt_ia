"""
Modelo de la base de datos para las Categorías de Incidentes.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from incident_api.db.base import Base


class IncidentCategory(Base):
    """
    Modelo ORM para la tabla `IncidentCategories`.

    Define las categorías de alto nivel para clasificar los incidentes,
    basado en taxonomías estándar como NIST SP 800-61.

    Atributos:
        incident_category_id (int): ID único de la categoría.
        name (str): Nombre de la categoría (ej: "Código Malicioso").
        description (str): Descripción de la categoría.

    Relaciones:
        incident_types: Relación uno-a-muchos con los tipos de incidentes específicos.
    """

    __tablename__ = "IncidentCategories"

    incident_category_id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Identificador único de la categoría de incidente.",
    )
    name = Column(
        String(255),
        nullable=False,
        unique=True,
        doc="Nombre único de la categoría de incidente.",
    )
    description = Column(
        String(512),
        nullable=True,
        doc="Descripción detallada de la categoría de incidente.",
    )

    # Relación con la tabla de Tipos de Incidente
    incident_types = relationship("IncidentType", back_populates="incident_category")
