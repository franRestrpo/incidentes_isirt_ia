from typing import List, Optional

from sqlalchemy.orm import Session

from incident_api.crud.base import CRUDBase
from incident_api.models import AvailableAIModel
from incident_api.schemas.ai_settings import (
    AvailableAIModelCreate,
    AvailableAIModelInDB as AvailableAIModelSchema,
)


class CRUDAvailableAIModel(
    CRUDBase[AvailableAIModel, AvailableAIModelCreate, AvailableAIModelSchema]
):
    def get_multi_by_provider(
        self, db: Session, *, provider: Optional[str] = None
    ) -> List[AvailableAIModel]:
        query = db.query(self.model)
        if provider:
            query = query.filter(self.model.provider == provider)
        return query.all()


available_ai_model = CRUDAvailableAIModel(AvailableAIModel)
