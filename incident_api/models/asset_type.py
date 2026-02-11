"""
Modelo de la base de datos para los Tipos de Activo.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from incident_api.db.base import Base


class AssetType(Base):
    """
    Modelo ORM para la tabla `AssetTypes`.

    Agrupa los activos en categorías lógicas de alto nivel para facilitar
    la clasificación y la selección en la interfaz de usuario.

    Atributos:
        asset_type_id (int): Identificador único del tipo de activo.
        name (str): Nombre del tipo de activo (ej: "Servicios Digitales").
        description (str): Descripción opcional del tipo de activo.

    Relaciones:
        assets: Relación uno-a-muchos con los activos que pertenecen a este tipo.
    """

    __tablename__ = "AssetTypes"

    asset_type_id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Identificador único del tipo de activo.",
    )
    name = Column(
        String(255),
        nullable=False,
        unique=True,
        doc="Nombre único del tipo de activo.",
    )
    description = Column(
        String(512),
        nullable=True,
        doc="Descripción detallada del tipo de activo.",
    )

    # Relación con la tabla de Activos
    assets = relationship("Asset", back_populates="asset_type")
