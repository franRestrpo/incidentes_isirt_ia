"""Utilidades para el hashing y verificación de contraseñas."""
from passlib.context import CryptContext

# Contexto para el hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Make SURE this class exists and is spelled EXACTLY like this.
class Hasher:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica si una contraseña plana coincide con su hash."""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            # Return False for any verification error (invalid hash, etc.)
            return False

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Genera el hash de una contraseña."""
        return pwd_context.hash(password)
