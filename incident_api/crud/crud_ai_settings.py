"""
Operaciones CRUD para los modelos de configuración de IA.
"""

from sqlalchemy.orm import Session
from typing import Optional, List

from incident_api.crud.base import CRUDBase
from incident_api.models.ai import AIModelSettings, AvailableAIModel
from incident_api.schemas.ai_settings import (
    AISettingsCreate,
    AISettingsUpdate,
    AvailableAIModelCreate,
)

# --- CRUD para AIModelSettings ---


class CRUDAISettings(CRUDBase[AIModelSettings, AISettingsCreate, AISettingsUpdate]):
    """
    Clase CRUD para AIModelSettings.
    Como se espera que solo haya una fila, se añade un método para obtener la configuración activa.
    """

    def get_active_settings(self, db: Session) -> AIModelSettings:
        """Obtiene la primera (y única) fila de configuración de IA."""
        # Devuelve la primera configuración que encuentre, o crea una por defecto si no existe.
        db_settings = db.query(self.model).first()
        if not db_settings:
            db_settings = self.create(db, obj_in=AISettingsCreate())
        return db_settings


# --- CRUD para AvailableAIModel ---


class CRUDAvailableAIModel(
    CRUDBase[AvailableAIModel, AvailableAIModelCreate, AvailableAIModelCreate]
):
    """
    Clase CRUD para AvailableAIModel.
    """

    def get_multi_by_provider(
        self, db: Session, *, provider: Optional[str] = None
    ) -> List[AvailableAIModel]:
        """
        Obtiene una lista de modelos de IA disponibles, opcionalmente filtrados por proveedor.
        """
        query = db.query(self.model)
        if provider:
            query = query.filter(self.model.provider == provider)
        return query.all()


ai_settings = CRUDAISettings(AIModelSettings)
available_ai_model = CRUDAvailableAIModel(AvailableAIModel)
