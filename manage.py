"""
Centro de control para la gestión de la aplicación de incidentes.

Este script proporciona una interfaz de línea de comandos (CLI) para realizar
tareas administrativas, de configuración y de prueba.
"""

# ==============================================================================
# IMPORTACIONES
# ==============================================================================
import sys
import os
import typer
import subprocess
import requests
import json
from datetime import datetime

# --- Configuración de la ruta del proyecto para permitir importaciones locales ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from incident_api.db.database import SessionLocal
from sqlalchemy.orm import Session
from incident_api.core.config import settings
from incident_api.core.hashing import Hasher
from incident_api import crud, schemas # Importar crud y schemas directamente
from incident_api.schemas.user import UserCreate
from incident_api.schemas.ai_settings import AvailableAIModelCreate, AISettingsCreate
from incident_api.schemas.group import GroupCreate
from incident_api.schemas.rag_settings import RAGSettingsCreate
from incident_api.crud import crud_user, available_ai_model, crud_group, crud_ai_settings, crud_rag_settings
from incident_api.services import user_service
from incident_api.ai.rag_processor import RAGProcessor

# ==============================================================================
# INICIALIZACIÓN DE LA APLICACIÓN TYPER (CLI)
# ==============================================================================
app = typer.Typer(
    name="manage",
    help='"""Gestiona la aplicación de gestión de incidentes, incluyendo configuración, seeding y pruebas."""',
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="markdown"
)

# ==============================================================================
# LÓGICA DE SEEDING (antes en seed_data.py)
# ==============================================================================
def seed_master_data_func(db: Session) -> None:
    """Puebla la base de datos con los datos de clasificación iniciales."""
    typer.echo("Iniciando el proceso de seeding...")

    # --- 1. Tipos de Activo ---
    asset_types = [
        {"name": "Servicios Digitales", "description": "Servicios de TI como correo, VPN, etc."},
        {"name": "Aplicaciones de Negocio", "description": "Software crítico para la operación.",},
        {"name": "Bases de Datos", "description": "Repositorios de datos de la organización."},
        {"name": "Infraestructura de Red", "description": "Switches, routers, firewalls, etc."},
        {"name": "Servidores", "description": "Servidores físicos o virtuales."},
        {"name": "Equipos de Usuario Final", "description": "Laptops, desktops, móviles."},
        {"name": "Ubicaciones Físicas", "description": "Oficinas, centros de datos, etc."},
        {"name": "Otro", "description": "Activos no clasificados en otras categorías."}
    ]
    for asset_type in asset_types:
        db_asset_type = crud.asset_type.get_by_name(db, name=asset_type["name"])
        if not db_asset_type:
            crud.asset_type.create(db, obj_in=schemas.AssetTypeCreate(**asset_type))
            typer.echo(f"  Creado Tipo de Activo: {asset_type['name']}")

    # --- 2. Categorías de Incidentes (Basado en NIST) ---
    incident_categories = [
        {"name": "CAT-1: Acceso No Autorizado", "description": "Eventos de compromiso de cuentas, escalada de privilegios, etc."},
        {"name": "CAT-2: Código Malicioso", "description": "Ransomware, virus, spyware, troyanos."},
        {"name": "CAT-3: Denegación de Servicio (DoS)", "description": "Ataques que buscan agotar los recursos de un sistema."},
        {"name": "CAT-4: Reconocimiento y Escaneo", "description": "Actividad de escaneo de puertos, enumeración de vulnerabilidades."},
        {"name": "CAT-5: Uso Inapropiado", "description": "Violación de las políticas de uso aceptable de los recursos."},
        {"name": "CAT-6: Incidente Físico", "description": "Robo, daño o acceso no autorizado a instalaciones o equipos."},
        {"name": "CAT-7: Fuga o Exposición de Datos", "description": "Exposición no autorizada de información sensible."},
        {"name": "CAT-8: Falla de Equipo / Software", "description": "Incidentes no maliciosos pero que requieren respuesta."},
    ]
    for category in incident_categories:
        db_category = crud.incident_category.get_by_name(db, name=category["name"])
        if not db_category:
            crud.incident_category.create(db, obj_in=schemas.IncidentCategoryCreate(**category))
            typer.echo(f"  Creada Categoría de Incidente: {category['name']}")

    # --- 3. Vectores de Ataque ---
    attack_vectors = [
        {"name": "VEC-1: Correo Electrónico (Phishing / Adjunto)", "description": "Ataques originados por email."},
        {"name": "VEC-2: Explotación de Vulnerabilidad Web", "description": "Inyección SQL, XSS, etc., en aplicaciones web."},
        {"name": "VEC-3: Dispositivo Extraíble", "description": "USB, discos duros externos, etc., infectados."},
        {"name": "VEC-4: Ingeniería Social", "description": "Engaño a través de llamadas, mensajes o en persona."},
        {"name": "VEC-5: Contraseña Débil / Adivinada", "description": "Ataques de fuerza bruta, reutilización de contraseñas."},
        {"name": "VEC-6: Conexión Inalámbrica Insegura", "description": "Ataques a través de redes Wi-Fi vulnerables."},
        {"name": "VEC-7: Acceso Físico No Autorizado", "description": "Entrada no autorizada a instalaciones."},
        {"name": "VEC-8: Amenaza Interna", "description": "Usuario con privilegios que abusa de su acceso, intencional o no."},
        {"name": "VEC-9: Falla de Configuración", "description": "Sistemas mal configurados que exponen vulnerabilidades."},
        {"name": "VEC-10: Desconocido", "description": "El vector de ataque no ha podido ser determinado."}
    ]
    for vector in attack_vectors:
        db_vector = crud.attack_vector.get_by_name(db, name=vector["name"])
        if not db_vector:
            crud.attack_vector.create(db, obj_in=schemas.AttackVectorCreate(**vector))
            typer.echo(f"  Creado Vector de Ataque: {vector['name']}")

    typer.echo("Proceso de seeding finalizado.")

# ==============================================================================
# LÓGICA DE PRUEBAS DE LOGIN (antes en test_login.py)
# ==============================================================================
API_BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "isirt@ips.com"
TEST_PASSWORD = "isirt_password"

def _test_health_check():
    typer.echo("\n❤️  Probando health check...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            typer.secho("✅ Health check OK", fg=typer.colors.GREEN)
            return True
        else:
            typer.secho(f"❌ Health check falló: {response.status_code}", fg=typer.colors.RED)
            return False
    except Exception as e:
        typer.secho(f"❌ Error en health check: {e}", fg=typer.colors.RED)
        return False

def _test_debug_endpoint():
    typer.echo("🔍 Probando endpoint de debugging...")
    try:
        response = requests.get(f"{API_BASE_URL}/login/debug")
        if response.status_code == 200:
            data = response.json()
            typer.secho("✅ Endpoint de debug funcionando", fg=typer.colors.GREEN)
            typer.echo(f"   Entorno: {data.get('environment', 'N/A')}")
            typer.echo(f"   Debug mode: {data.get('server_info', {}).get('debug_mode', 'N/A')}")
            return True
        elif response.status_code == 403:
            typer.secho("⚠️  Endpoint de debug deshabilitado (modo producción)", fg=typer.colors.YELLOW)
            return True
        else:
            typer.secho(f"❌ Error en endpoint de debug: {response.status_code}", fg=typer.colors.RED)
            return False
    except Exception as e:
        typer.secho(f"❌ Error conectando al endpoint de debug: {e}", fg=typer.colors.RED)
        return False

def _test_login():
    typer.echo("\n🔐 Probando login...")
    try:
        data = {"username": TEST_EMAIL, "password": TEST_PASSWORD}
        response = requests.post(f"{API_BASE_URL}/login/token", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        if response.status_code == 200:
            result = response.json()
            typer.secho("✅ Login exitoso", fg=typer.colors.GREEN)
            typer.echo(f"   Token generado: {result.get('access_token', '')[:20]}...")
            typer.echo(f"   Tipo: {result.get('token_type', 'N/A')}")
            return True
        else:
            typer.secho(f"❌ Login falló: {response.status_code}", fg=typer.colors.RED)
            try:
                error = response.json()
                typer.echo(f"   Detalle: {error.get('detail', 'Sin detalle')}")
            except:
                typer.echo(f"   Respuesta: {response.text}")
            return False
    except Exception as e:
        typer.secho(f"❌ Error en login: {e}", fg=typer.colors.RED)
        return False

def _test_invalid_login():
    typer.echo("\n🚫 Probando login con credenciales inválidas...")
    try:
        data = {"username": "invalid@email.com", "password": "wrongpassword"}
        response = requests.post(f"{API_BASE_URL}/login/token", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        if response.status_code == 401:
            typer.secho("✅ Manejo correcto de credenciales inválidas", fg=typer.colors.GREEN)
            try:
                error = response.json()
                typer.echo(f"   Mensaje: {error.get('detail', 'Sin detalle')}")
            except:
                typer.echo("   Respuesta sin formato JSON")
            return True
        else:
            typer.secho(f"❌ Respuesta inesperada: {response.status_code}", fg=typer.colors.RED)
            return False
    except Exception as e:
        typer.secho(f"❌ Error en login inválido: {e}", fg=typer.colors.RED)
        return False

# ==============================================================================
# DEFINICIÓN DE COMANDOS CLI (TYPER)
# ==============================================================================
@app.command()
def test_login():
    """Ejecuta un conjunto de pruebas contra los endpoints de login para verificar su estado."""
    typer.secho("🚀 Iniciando pruebas del sistema de login", bold=True)
    typer.echo(f"📅 Timestamp: {datetime.now().isoformat()}")
    typer.echo(f"🌐 API URL: {API_BASE_URL}")
    typer.echo("-" * 50)

    tests = [
        ("Health Check", _test_health_check),
        ("Debug Endpoint", _test_debug_endpoint),
        ("Login Válido", _test_login),
        ("Login Inválido", _test_invalid_login),
    ]
    results = [(name, func()) for name, func in tests]

    typer.echo("\n" + "=" * 50)
    typer.secho("📊 RESULTADOS FINALES", bold=True)
    typer.echo("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = typer.style("✅ PASÓ", fg=typer.colors.GREEN) if result else typer.style("❌ FALLÓ", fg=typer.colors.RED)
        typer.echo(f"{test_name}: {status}")

    typer.echo("-" * 50)
    typer.echo(f"Tests pasados: {passed}/{total}")

    if passed != total:
        typer.secho("⚠️  Algunas pruebas fallaron. Revisa los logs para más detalles.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)
    else:
        typer.secho("🎉 ¡Todas las pruebas pasaron exitosamente!", fg=typer.colors.GREEN)


@app.command()
def reset_superuser():
    """
    Restablece la contraseña del superusuario basado en las variables de entorno.
    Útil si la contraseña se olvida o necesita ser rotada.
    """
    db: Session = SessionLocal()
    try:
        typer.secho(f"Attempting to reset password for superuser '{settings.FIRST_SUPERUSER_EMAIL}'...", fg=typer.colors.YELLOW)
        user = crud_user.user.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
        if not user:
            typer.secho(f"Error: Superuser '{settings.FIRST_SUPERUSER_EMAIL}' not found.", fg=typer.colors.RED)
            typer.secho("Please create the user first with 'create-superuser'.", fg=typer.colors.BLUE)
            raise typer.Exit(code=1)

        new_password = settings.FIRST_SUPERUSER_PASSWORD
        user.hashed_password = Hasher.get_password_hash(new_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        typer.secho(f"Password for superuser '{settings.FIRST_SUPERUSER_EMAIL}' has been reset successfully.", fg=typer.colors.GREEN)
    finally:
        db.close()


@app.command()
def run_migrations():
    """
    Ejecuta las migraciones de la base de datos usando Alembic.
    """
    typer.secho("Running database migrations...", fg=typer.colors.YELLOW)
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True, capture_output=True, text=True)
        typer.secho("Migrations applied successfully.", fg=typer.colors.GREEN)
    except subprocess.CalledProcessError as e:
        typer.secho(f"Error applying migrations: {e.stderr}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command()
def seed_data():
    """
    Puebla la BD con datos maestros iniciales (categorías, vectores, etc.).
    """
    db: Session = SessionLocal()
    try:
        typer.secho("Populating database with initial master data...", fg=typer.colors.YELLOW)
        seed_master_data_func(db)
        typer.secho("Master data seeding completed.", fg=typer.colors.GREEN)
    finally:
        db.close()

@app.command()
def create_superuser():
    """
    Crea el superusuario inicial a partir de las variables de entorno.
    """
    db: Session = SessionLocal()
    try:
        typer.secho("Creating superuser from environment variables...", fg=typer.colors.YELLOW)
        user = crud_user.user.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
        if not user:
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER_EMAIL,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                full_name=settings.FIRST_SUPERUSER_FULL_NAME,
                role="Administrador"
            )
            user_service.create_user(db=db, user_in=user_in)
            typer.secho(f"Superuser '{settings.FIRST_SUPERUSER_EMAIL}' created.", fg=typer.colors.GREEN)
        else:
            typer.secho(f"Superuser '{settings.FIRST_SUPERUSER_EMAIL}' already exists.", fg=typer.colors.BLUE)
    finally:
        db.close()

@app.command()
def create_user():
    """
    Crea un nuevo usuario de forma interactiva.
    """
    db: Session = SessionLocal()
    try:
        typer.secho("Creating a new user interactively...", fg=typer.colors.CYAN)
        email = typer.prompt("Email")
        if crud_user.user.get_by_email(db, email=email):
            typer.secho(f"Error: User '{email}' already exists.", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        full_name = typer.prompt("Full Name")
        password = typer.prompt("Password", hide_input=True, confirmation_prompt=True)
        roles = ["Empleado", "Miembro IRT", "Líder IRT", "Administrador"]
        role_menu = "\n".join([f"{i+1}. {r}" for i, r in enumerate(roles)])
        typer.echo("Select a role:\n" + role_menu)
        role_choice = typer.prompt("Role number", type=int)
        if not 1 <= role_choice <= len(roles):
            typer.secho("Invalid role selection.", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        role = roles[role_choice - 1]

        user_in = UserCreate(email=email, password=password, full_name=full_name, role=role)
        user_service.create_user(db=db, user_in=user_in)
        typer.secho(f"User '{email}' created successfully.", fg=typer.colors.GREEN)
    finally:
        db.close()

@app.command()
def create_default_groups():
    """
    Crea los grupos predeterminados para la organización.
    """
    db: Session = SessionLocal()
    try:
        typer.secho("Creating default groups...", fg=typer.colors.YELLOW)
        default_groups = [
            {"name": "Administradores", "description": "Grupo de administradores del sistema"},
            {"name": "IRT Principal", "description": "Equipo de respuesta a incidentes principal"},
            {"name": "Desarrollo", "description": "Equipo de desarrollo de software"},
            {"name": "Seguridad", "description": "Equipo de seguridad de la información"},
        ]

        for group_data in default_groups:
            existing_group = crud_group.group.get_by_name(db, name=group_data["name"])
            if not existing_group:
                group_in = GroupCreate(**group_data)
                crud_group.group.create(db, obj_in=group_in)
                typer.secho(f"  Created group: {group_data['name']}", fg=typer.colors.GREEN)
            else:
                typer.secho(f"  Group already exists: {group_data['name']}", fg=typer.colors.BLUE)
        typer.secho("Default groups creation completed.", fg=typer.colors.GREEN)
    finally:
        db.close()

@app.command()
def populate_ai_models():
    """
    Añade y actualiza la lista de modelos de IA disponibles en la BD.
    """
    db: Session = SessionLocal()
    try:
        models_to_add = {
            "gemini": ["gemini-2.0-flash-lite", "gemini-2.0-flash","gemini-2.5-flash-lite"],
            "openai": ["gpt-3.5-turbo", "gpt-4o", "gpt-4-turbo"],
            "ollama": ["llama3:latest", "llama3.1:latest", "llama3.2:3b", "llama3-groq-tool-use:8b", "mistral:latest", "gemma:2b","phi3:latest","dolphin3:latest"],
            "groq": ["llama-3.1-8b-instant", "openai/gpt-oss-20b", "meta-llama/llama-4-maverick-17b-128e-instruct"],
        }

        existing_models = {m.model_name for m in available_ai_model.get_multi(db)}
        typer.secho("Populating AI models...", fg=typer.colors.YELLOW)

        for provider, model_names in models_to_add.items():
            for model_name in model_names:
                if model_name not in existing_models:
                    model_data = AvailableAIModelCreate(provider=provider, model_name=model_name)
                    available_ai_model.create(db, obj_in=model_data)
                    typer.secho(f"  Added: {model_name} ({provider})", fg=typer.colors.GREEN)
                else:
                    typer.secho(f"  Skipped (already exists): {model_name} ({provider})", fg=typer.colors.BLUE)
        typer.secho("AI models population completed.", fg=typer.colors.YELLOW)
    finally:
        db.close()

@app.command()
def create_default_ai_settings():
    """
    Crea la configuración predeterminada de IA y RAG.
    """
    db: Session = SessionLocal()
    try:
        typer.secho("Creating default AI settings...", fg=typer.colors.YELLOW)

        # Verificar si la configuración de IA ya existe
        existing_ai = crud_ai_settings.ai_settings.get_active_settings(db)
        if existing_ai:
            typer.secho("AI settings already exist.", fg=typer.colors.BLUE)
        else:
            # Crear configuración de IA predeterminada
            ai_settings = AISettingsCreate(
                provider="gemini",
                model_name="gemini-2.0-flash-lite",
                model_params={"temperature": 0.7, "max_tokens": 1000},
                is_active=True
            )
            crud_ai_settings.ai_settings.create(db, obj_in=ai_settings)
            typer.secho("Default AI settings created.", fg=typer.colors.GREEN)

        # Verificar si la configuración de RAG ya existe
        existing_rag = crud_rag_settings.rag_settings.get_active_settings(db)
        if existing_rag:
            typer.secho("RAG settings already exist.", fg=typer.colors.BLUE)
        else:
            # Crear configuración de RAG predeterminada
            rag_settings = RAGSettingsCreate(
                embedding_model="gemini-2.0-flash-lite",
                index_path="faiss_index",
                chunk_size=1000,
                chunk_overlap=200,
                is_active=True
            )
            crud_rag_settings.rag_settings.create(db, obj_in=rag_settings)
            typer.secho("Default RAG settings created.", fg=typer.colors.GREEN)

        typer.secho("Default AI and RAG settings creation completed.", fg=typer.colors.GREEN)
    finally:
        db.close()

@app.command()
def ingest_playbooks():
    """
    Procesa los 'playbooks' y crea/actualiza el índice FAISS para RAG.
    """
    playbooks_dir = "playbooks"
    typer.secho(f"Ensuring '{playbooks_dir}' directory exists...", fg=typer.colors.YELLOW)
    os.makedirs(playbooks_dir, exist_ok=True)

    typer.secho("Ingesting playbook documents for RAG...", fg=typer.colors.YELLOW)
    try:
        rag_processor = RAGProcessor()
        rag_processor.ingest_documents()
        typer.secho("Playbook ingestion finished successfully.", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Error during playbook ingestion: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command()
def initial_setup():
    """
    Ejecuta todos los pasos de configuración inicial en orden.
    """
    typer.secho("--- Starting Initial Application Setup ---", bold=True, fg=typer.colors.CYAN)
    typer.secho("\n[Step 1/7] Running database migrations...", bold=True)
    run_migrations()
    typer.secho("\n[Step 2/7] Populating database with master data...", bold=True)
    seed_data()
    typer.secho("\n[Step 3/7] Creating default groups...", bold=True)
    create_default_groups()
    typer.secho("\n[Step 4/7] Creating superuser...", bold=True)
    create_superuser()
    typer.secho("\n[Step 5/7] Populating AI models...", bold=True)
    populate_ai_models()
    typer.secho("\n[Step 6/7] Creating default AI settings...", bold=True)
    create_default_ai_settings()
    typer.secho("\n[Step 7/7] Ingesting playbooks for RAG...", bold=True)
    ingest_playbooks()
    typer.secho("\n--- Initial Setup Finished ---", bold=True, fg=typer.colors.GREEN)

# ==============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# ==============================================================================
if __name__ == "__main__":
    app()
