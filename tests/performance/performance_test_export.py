#!/usr/bin/env python3
"""
Script de prueba de rendimiento para la funcionalidad de exportación de usuarios.
"""

import time
import requests
from concurrent.futures import ThreadPoolExecutor
import sys

# Configuración
API_BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@example.com"  # Ajustar según el usuario admin existente
ADMIN_PASSWORD = "your_admin_password"  # Ajustar según la contraseña

def login():
    """Autenticar y obtener token."""
    response = requests.post(f"{API_BASE_URL}/login/token", data={
        "username": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Error en login: {response.status_code} - {response.text}")
        sys.exit(1)

def create_users(token, num_users):
    """Crear usuarios de prueba."""
    headers = {"Authorization": f"Bearer {token}"}
    users_created = 0

    for i in range(num_users):
        user_data = {
            "email": f"user{i}@test.com",
            "password": "your_test_password",
            "full_name": f"User {i}",
            "role": "Empleado"
        }
        response = requests.post(f"{API_BASE_URL}/users/", headers=headers, json=user_data)
        if response.status_code == 201:
            users_created += 1
        else:
            print(f"Error creando usuario {i}: {response.status_code}")

    print(f"Usuarios creados: {users_created}")
    return users_created

def test_export_performance(token, format_type, num_requests=10):
    """Probar rendimiento de exportación."""
    headers = {"Authorization": f"Bearer {token}"}

    def single_export():
        start_time = time.time()
        response = requests.get(f"{API_BASE_URL}/users/export?format={format_type}", headers=headers)
        end_time = time.time()
        if response.status_code == 200:
            return end_time - start_time
        else:
            print(f"Error en export: {response.status_code}")
            return None

    print(f"Probando exportación en formato {format_type} con {num_requests} solicitudes...")

    with ThreadPoolExecutor(max_workers=5) as executor:
        times = list(executor.map(lambda _: single_export(), range(num_requests)))

    valid_times = [t for t in times if t is not None]
    if valid_times:
        avg_time = sum(valid_times) / len(valid_times)
        min_time = min(valid_times)
        max_time = max(valid_times)
        print(f"Promedio: {avg_time:.3f}s")
        print(f"Mínimo: {min_time:.3f}s")
        print(f"Máximo: {max_time:.3f}s")
        return avg_time
    else:
        print("No se pudieron completar las pruebas")
        return None

def main():
    print("Iniciando pruebas de rendimiento de exportación de usuarios...")

    # Login
    token = login()
    print("Login exitoso")

    # Crear usuarios de prueba
    num_users = 100
    print(f"Creando {num_users} usuarios de prueba...")
    create_users(token, num_users)

    # Probar exportación
    formats = ["json", "csv", "xml"]
    results = {}

    for fmt in formats:
        results[fmt] = test_export_performance(token, fmt)

    print("\nResumen de rendimiento:")
    for fmt, avg_time in results.items():
        if avg_time:
            print(f"Formato {fmt}: {avg_time:.3f}s (promedio)")

if __name__ == "__main__":
    main()
