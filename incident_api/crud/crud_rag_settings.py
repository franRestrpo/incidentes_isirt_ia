"""
Operaciones CRUD para el modelo de configuración de RAG.
"""

from incident_api.crud.base import CRUDBase
from incident_api.models.ai import RAGSettings
from incident_api.schemas.rag_settings import RAGSettingsCreate, RAGSettingsUpdate

class CRUDRAGSettings(CRUDBase[RAGSettings, RAGSettingsCreate, RAGSettingsUpdate]):
    """
    Clase CRUD para RAGSettings.
    Se espera que solo haya una fila, por lo que se añade un método para obtener la config activa.
    """
    def get_active_settings(self, db) -> RAGSettings:
        db_settings = db.query(self.model).first()
        if not db_settings:
            db_settings = self.create(db, obj_in=RAGSettingsCreate())
        return db_settings

rag_settings = CRUDRAGSettings(RAGSettings)
