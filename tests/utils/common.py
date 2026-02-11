"""
Funciones de utilidad comunes para las pruebas.
"""

import random
import string


def random_lower_string(length: int = 32) -> str:
    """Genera una cadena aleatoria en minúsculas."""
    return "".join(random.choices(string.ascii_lowercase, k=length))


def random_email() -> str:
    """Genera un email aleatorio."""
    return f"{random_lower_string(10)}@{random_lower_string(8)}.com"
