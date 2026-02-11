"""
Servicio para la lógica de negocio relacionada con la configuración de RAG.
"""

from sqlalchemy.orm import Session
from incident_api import crud, models, schemas

class RAGSettingsService:
    def get_settings(self, db: Session) -> models.RAGSettings:
        return crud.rag_settings.get_active_settings(db)

    def update_settings(
        self, db: Session, settings_in: schemas.RAGSettingsUpdate
    ) -> models.RAGSettings:
        db_settings = self.get_settings(db)
        return crud.rag_settings.update(db, db_obj=db_settings, obj_in=settings_in)

rag_settings_service = RAGSettingsService()
