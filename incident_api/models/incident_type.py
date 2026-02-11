"""
Modelo de la base de datos para los Tipos de Incidentes.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from incident_api.db.base import Base


class IncidentType(Base):
    """
    Modelo ORM para la tabla `IncidentTypes`.

    Define los tipos de incidentes específicos, cada uno asociado a una
    categoría de alto nivel.

    Atributos:
        incident_type_id (int): ID único del tipo de incidente.
        name (str): Nombre del tipo (ej: "Ransomware").
        description (str): Descripción del tipo de incidente.
        incident_category_id (int): Clave foránea a la categoría del incidente.

    Relaciones:
        incident_category: Relación muchos-a-uno con la categoría del incidente.
    """

    __tablename__ = "IncidentTypes"

    incident_type_id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Identificador único del tipo de incidente.",
    )
    name = Column(
        String(255), nullable=False, unique=True, doc="Nombre único del tipo de incidente."
    )
    description = Column(
        String(512), nullable=True, doc="Descripción detallada del tipo de incidente."
    )
    incident_category_id = Column(
        Integer,
        ForeignKey("IncidentCategories.incident_category_id"),
        nullable=False,
        doc="ID de la categoría de incidente a la que pertenece.",
    )

    # Relación con la tabla IncidentCategories
    incident_category = relationship(
        "IncidentCategory", back_populates="incident_types"
    )
