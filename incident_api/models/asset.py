"""
Modelo de la base de datos para los Activos de la organización.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from incident_api.db.base import Base


class Asset(Base):
    """
    Modelo ORM para la tabla `Assets`.

    Almacena los activos de la organización que pueden ser afectados por un incidente.
    Cada activo pertenece a un tipo de activo para facilitar la clasificación.

    Atributos:
        asset_id (int): Identificador único del activo.
        name (str): Nombre del activo (ej: "Servidor de Correo Principal").
        description (str): Descripción detallada del activo.
        asset_type_id (int): Clave foránea al tipo de activo al que pertenece.

    Relaciones:
        asset_type: Relación muchos-a-uno con el tipo de activo.
    """

    __tablename__ = "Assets"

    asset_id = Column(
        Integer, primary_key=True, index=True, doc="Identificador único del activo."
    )
    name = Column(
        String(255), nullable=False, unique=True, doc="Nombre único del activo."
    )
    description = Column(
        String(512), nullable=True, doc="Descripción detallada del activo."
    )
    asset_type_id = Column(
        Integer,
        ForeignKey("AssetTypes.asset_type_id"),
        nullable=False,
        doc="ID del tipo de activo al que pertenece.",
    )

    # Relación con la tabla AssetTypes
    asset_type = relationship("AssetType", back_populates="assets")
