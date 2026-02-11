"""
Modelo de la base de datos para los Archivos de Evidencia.

Este módulo define el modelo `EvidenceFile`, que representa la tabla `EvidenceFiles`.
Se utiliza para almacenar metadatos sobre los archivos cargados como evidencia
para un incidente de seguridad.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from incident_api.db.base import Base


class EvidenceFile(Base):
    """
    Modelo ORM para la tabla `EvidenceFiles`.

    Almacena la información de referencia de cada archivo de evidencia subido al sistema,
    vinculándolo a un incidente y al usuario que lo cargó.

    Atributos:
        file_id (int): Identificador único del archivo.
        incident_id (int): ID del incidente al que está asociado el archivo.
        uploaded_by_id (int): ID del usuario que subió el archivo.
        file_name (str): Nombre original del archivo.
        file_path (str): Ruta de almacenamiento del archivo en el servidor.
        file_type (str): Tipo MIME del archivo (e.g., 'image/png').
        file_size_bytes (int): Tamaño del archivo en bytes.
        uploaded_at (datetime): Fecha y hora en que se subió el archivo.

    Relaciones:
        incident: Relación con el incidente al que pertenece.
        uploader: Relación con el usuario que subió el archivo.
    """

    __tablename__ = "EvidenceFiles"

    file_id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Identificador único del archivo de evidencia.",
    )
    incident_id = Column(
        Integer,
        ForeignKey("Incidents.incident_id"),
        nullable=False,
        doc="ID del incidente asociado.",
    )
    uploaded_by_id = Column(
        Integer,
        ForeignKey("Users.user_id"),
        nullable=False,
        doc="ID del usuario que subió el archivo.",
    )

    file_name = Column(String(255), nullable=False, doc="Nombre original del archivo.")
    file_path = Column(
        String(512), nullable=False, doc="Ruta de almacenamiento del archivo."
    )
    file_type = Column(String(100), nullable=False, doc="Tipo MIME del archivo.")
    file_size_bytes = Column(
        Integer, nullable=False, doc="Tamaño del archivo en bytes."
    )
    uploaded_at = Column(
        DateTime, server_default=func.now(), doc="Fecha y hora de carga del archivo."
    )
    file_hash = Column(String(256), nullable=True, doc="Hash del contenido del archivo para verificación de integridad.")

    # Relaciones con las tablas Incident y User
    incident = relationship("Incident", back_populates="evidence_files")
    uploader = relationship("User", back_populates="uploaded_files")
