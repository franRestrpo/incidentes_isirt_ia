"""Operaciones CRUD para el modelo EvidenceFile."""

from sqlalchemy.orm import Session
from typing import List

from incident_api.crud.base import CRUDBase
from incident_api.models.evidence_file import EvidenceFile
from incident_api.schemas.evidence_file import EvidenceFileCreate


class CRUDEvidenceFile(
    CRUDBase[EvidenceFile, EvidenceFileCreate, EvidenceFileCreate]
):  # No update schema
    """Clase CRUD para el modelo EvidenceFile."""

    def create_with_incident_and_uploader(
        self,
        db: Session,
        *,
        obj_in: EvidenceFileCreate,
        incident_id: int,
        uploader_id: int,
        file_path: str
    ) -> EvidenceFile:
        """Crea un nuevo registro de archivo de evidencia."""
        obj_in_data = obj_in.dict()
        db_obj = self.model(
            **obj_in_data,
            incident_id=incident_id,
            uploaded_by_id=uploader_id,
            file_path=file_path
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_incident(self, db: Session, *, incident_id: int) -> List[EvidenceFile]:
        """Obtiene todos los archivos de evidencia para un incidente específico."""
        return db.query(self.model).filter(self.model.incident_id == incident_id).all()

    def count_by_uploader(self, db: Session, *, user_id: int) -> int:
        """Counts the total number of files uploaded by a user."""
        return db.query(self.model).filter(self.model.uploaded_by_id == user_id).count()


evidence_file = CRUDEvidenceFile(EvidenceFile)
