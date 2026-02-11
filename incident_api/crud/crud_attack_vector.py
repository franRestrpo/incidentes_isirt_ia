"""
Operaciones CRUD para el modelo AttackVector.
"""

from incident_api.crud.base import CRUDBase
from incident_api.models.attack_vector import AttackVector
from incident_api.schemas.attack_vector import AttackVectorCreate, AttackVectorCreate


class CRUDAttackVector(CRUDBase[AttackVector, AttackVectorCreate, AttackVectorCreate]):
    """Clase CRUD para el modelo AttackVector."""

    pass


attack_vector = CRUDAttackVector(AttackVector)
