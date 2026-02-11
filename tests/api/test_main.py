"""
Pruebas para los endpoints principales de la aplicación (ej. health check).
"""

from fastapi.testclient import TestClient

def test_health_check(test_client: TestClient):
    """
    Verifica que el endpoint /health funcione correctamente.
    """
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
