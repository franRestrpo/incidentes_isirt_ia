# Guía de Debugging - Sistema de Login

## Información General

El sistema de login ha sido mejorado con logging detallado y configuración específica por entorno para facilitar la resolución de problemas.

## Configuración por Entorno

### Desarrollo
- **Archivo**: `config.dev.env`
- **Características**:
  - DEBUG=true
  - Logging detallado
  - Intentos de login: 10 (más permisivo)
  - Bloqueo: 5 minutos
  - Rate limit: 20 requests/10 minutos
  - Token expiration: 60 minutos

### Producción
- **Archivo**: `config.prod.env`
- **Características**:
  - DEBUG=false
  - Logging solo warnings/errors
  - Intentos de login: 3 (más restrictivo)
  - Bloqueo: 30 minutos
  - Rate limit: 5 requests/15 minutos
  - Token expiration: 15 minutos

## Endpoints de Debugging

### Información del Sistema (Solo Desarrollo)
```
GET /api/v1/login/debug
```
Proporciona información detallada del sistema para troubleshooting.

**Respuesta de ejemplo**:
```json
{
  "timestamp": "2025-01-14T17:25:00.000Z",
  "environment": "development",
  "client_ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "server_info": {
    "debug_mode": true,
    "project_name": "API de Gestión de Incidentes",
    "token_expiration_minutes": 60
  }
}
```

## Logs de Login

### Información Registrada

#### Login Exitoso
```
INFO - Login successful - IP: 192.168.1.100, Email: user@domain.com, UserID: 123, Role: ADMINISTRADOR
DEBUG - User authenticated successfully: user@domain.com (ID: 123)
DEBUG - Token generated for user: user@domain.com, Expires in: 60 minutes
```

#### Login Fallido
```
WARNING - Login failed - IP: 192.168.1.100, Email: user@domain.com, Reason: Invalid credentials or inactive user
DEBUG - Invalid password for user: user@domain.com
```

#### Errores del Sistema
```
ERROR - Login error - IP: 192.168.1.100, Email: user@domain.com, Error: Database connection failed
```

## Problemas Comunes y Soluciones

### 1. ERR_CONNECTION_RESET
**Síntomas**: Error de conexión al intentar hacer login
**Causas posibles**:
- API no está ejecutándose
- Problemas de red
- Puerto 8000 bloqueado

**Solución**:
```bash
# Verificar estado de contenedores
docker ps

# Reiniciar servicios
docker compose down && docker compose up -d

# Verificar logs
docker logs fastapi_api
```

### 2. Credenciales Inválidas
**Síntomas**: Error 401 con mensaje de credenciales incorrectas
**Debugging**:
1. Verificar email y contraseña en base de datos
2. Revisar logs para ver el motivo específico
3. Verificar si usuario está activo

### 3. Usuario Inactivo
**Síntomas**: Login falla sin motivo aparente
**Logs**: `DEBUG - Inactive user attempted login: user@domain.com`
**Solución**: Activar usuario en base de datos

### 4. Rate Limiting
**Síntomas**: Error 429 (Too Many Requests)
**Solución**: Esperar el tiempo especificado en configuración

### 5. Problemas de CORS
**Síntomas**: Error de CORS en navegador
**Verificación**: Revisar configuración de `CORS_ORIGINS` en archivo de entorno

## Configuración de Logging

### Desarrollo
- Console logging: INFO level
- File logging: DEBUG level (si está disponible)
- Información detallada en respuestas de error

### Producción
- Console logging: WARNING level
- File logging: ERROR level
- Mensajes de error genéricos (sin detalles sensibles)

## Variables de Entorno Importantes

```bash
# Configuración básica
DEBUG=true|false
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR

# Configuración de login
LOGIN_MAX_ATTEMPTS=5
LOGIN_LOCKOUT_MINUTES=15
LOGIN_RATE_LIMIT_REQUESTS=10
LOGIN_RATE_LIMIT_WINDOW_MINUTES=5

# Seguridad
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Testing del Sistema

### Verificar Configuración
```bash
# En desarrollo
curl http://localhost:8000/api/v1/login/debug

# Verificar logs
docker logs fastapi_api --tail 20
```

### Probar Login
```bash
curl -X POST "http://localhost:8000/api/v1/login/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@domain.com&password=password"
```

## Monitoreo Continuo

### Métricas a Monitorear
- Tasa de logins exitosos/fallidos
- Intentos de login por IP
- Errores de autenticación por tipo
- Uso de rate limiting

### Alertas Recomendadas
- Aumento significativo en logins fallidos
- Múltiples intentos desde misma IP
- Errores de conexión a base de datos
- Problemas de CORS

## Soporte

Para problemas específicos:
1. Revisar logs del contenedor: `docker logs fastapi_api`
2. Verificar configuración de entorno
3. Usar endpoint de debug en desarrollo
4. Revisar conectividad de red y base de datos