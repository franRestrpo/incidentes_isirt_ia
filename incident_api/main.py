"""Punto de entrada principal de la aplicación FastAPI."""
import traceback
import logging
import os

logger = logging.getLogger(__name__)
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from incident_api.core.logging_config import setup_logging
from incident_api.api.api import api_router
from incident_api.core.config import settings


# Setup logging
setup_logging()

def create_upload_dir():
    """Crea el directorio de subidas si no existe."""
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
)

# Registra la función en el evento 'startup'
app.add_event_handler("startup", create_upload_dir)


# --- Middlewares ---
# El orden es importante. El primer middleware añadido es el más externo.

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            logging.error(f"Unhandled exception for request {request.method} {request.url}: {exc}", exc_info=True)
            if settings.DEBUG:
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Internal Server Error",
                        "exception_type": str(type(exc).__name__),
                        "message": str(exc),
                    },
                )
            return JSONResponse(
                status_code=500,
                content={"error": "Internal Server Error"},
            )

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        import time
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"REQUEST - {request.method} {request.url.path} - IP: {client_ip}")
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            logger.info(f"RESPONSE - {request.method} {request.url.path} - Status: {response.status_code}, Time: {process_time:.2f}s")
            return response
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(f"ERROR during request - {request.method} {request.url.path} - Time: {process_time:.2f}s, Error: {str(exc)}")
            raise exc

# 1. Middleware de manejo de errores (más externo)
app.add_middleware(ErrorHandlingMiddleware)

# 2. Middleware de logging
app.add_middleware(RequestLoggingMiddleware)

# 3. Middleware de CORS
if settings.DEBUG:
    cors_origins = ["http://localhost", "http://localhost:8080", "http://localhost:8081", "http://127.0.0.1", "http://127.0.0.1:8080", "http://127.0.0.1:8081"]
else:
    cors_origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else []

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# 4. Middleware para el manejo de sesiones (necesario para OAuth)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get(f"{settings.API_V1_STR}", tags=["Root"])
async def read_root():
    """Endpoint raíz de la API. Devuelve un mensaje de bienvenida."""
    return {"message": "Bienvenido a la API de Gestión de Incidentes ISIRT"}


@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint de chequeo de salud. Devuelve un estado de 'ok'."""
    return {"status": "ok"}

