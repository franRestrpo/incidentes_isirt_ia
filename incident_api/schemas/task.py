"""
Esquemas de Pydantic para el modelo Task.
"""

from pydantic import BaseModel
from typing import Optional, Any, Dict


class AsyncTaskResponse(BaseModel):
    """Respuesta para una tarea asíncrona que ha sido iniciada."""
    task_id: str
    status: str


class AsyncTaskStatus(BaseModel):
    """Estado de una tarea asíncrona."""
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None


class TaskBase(BaseModel):
    """Esquema base con los campos comunes de una tarea."""

    task_id: str
    status: str
    result: Optional[Any] = None


class TaskCreate(TaskBase):
    """Esquema para la creación de una nueva tarea."""

    pass


class TaskUpdate(TaskBase):
    """Esquema para actualizar una tarea existente."""

    pass


class TaskInDB(TaskBase):
    """Esquema para representar una tarea tal como se devuelve desde la API."""

    id: int

    class Config:
        orm_mode = True