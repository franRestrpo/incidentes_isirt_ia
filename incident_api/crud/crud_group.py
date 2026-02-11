"""
Operaciones CRUD para el modelo Group.
"""
from typing import Optional
from sqlalchemy.orm import Session

from incident_api.models.group import Group
from incident_api.schemas.group import GroupCreate, GroupUpdate
from .base import CRUDBase


class CRUDGroup(CRUDBase[Group, GroupCreate, GroupUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Group]:
        return db.query(self.model).filter(self.model.name == name).first()

    def create(self, db: Session, *, obj_in: GroupCreate) -> Group:
        return super().create(db, obj_in=obj_in)


group = CRUDGroup(Group)