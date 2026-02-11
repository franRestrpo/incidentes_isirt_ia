"""
Operaciones CRUD para el modelo Task.
"""
from typing import Optional
from sqlalchemy.orm import Session
from incident_api.crud.base import CRUDBase
from incident_api.models.task import Task
from incident_api.schemas.task import TaskCreate, TaskUpdate


class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    """Clase CRUD para el modelo Task."""

    def get_by_task_id(self, db: Session, *, task_id: str) -> Optional[Task]:
        return db.query(Task).filter(Task.task_id == task_id).first()


task = CRUDTask(Task)
