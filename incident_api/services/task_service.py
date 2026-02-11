"""
Servicio para la lógica de negocio relacionada con las tareas en segundo plano.
"""

from typing import Optional
from sqlalchemy.orm import Session

from incident_api import crud, models, schemas


class TaskService:
    """
    Clase de servicio para gestionar la lógica de negocio de las tareas.
    """

    def get_task_by_task_id(self, db: Session, task_id: str) -> Optional[models.Task]:
        """
        Obtiene una tarea por su ID de tarea.
        """
        return crud.task.get_by_task_id(db, task_id=task_id)

    def create_task(self, db: Session, task_id: str) -> models.Task:
        """
        Crea una nueva tarea.
        """
        task_in = schemas.TaskCreate(task_id=task_id, status="pending")
        return crud.task.create(db, obj_in=task_in)

    def update_task(self, db: Session, task: models.Task, status: str, result: Optional[dict] = None) -> models.Task:
        """
        Actualiza el estado y el resultado de una tarea.
        """
        task_update = schemas.TaskUpdate(task_id=task.task_id, status=status, result=result)
        return crud.task.update(db, db_obj=task, obj_in=task_update)


task_service = TaskService()
