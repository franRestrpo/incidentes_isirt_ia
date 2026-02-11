# Guía de Monitoreo de Logging - Sistema ISIRT

## Información General

Esta guía proporciona directrices para monitorear y analizar los logs del sistema ISIRT, enfocándose en la trazabilidad de operaciones críticas como autenticación, servicios de IA y operaciones de negocio.

## Arquitectura de Logging

### Niveles de Logging

#### Backend (Python/FastAPI)
- **DEBUG**: Información detallada para desarrollo y troubleshooting
- **INFO**: Eventos importantes del sistema (logins, operaciones de IA)
- **WARNING**: Situaciones que requieren atención pero no son errores
- **ERROR**: Errores que afectan la funcionalidad

#### Frontend (JavaScript)
- **DEBUG**: Información detallada de operaciones
- **INFO**: Eventos importantes del usuario
- **WARN**: Advertencias de operaciones
- **ERROR**: Errores que afectan la experiencia del usuario

## Eventos Críticos a Monitorear

### 1. Autenticación

#### Eventos de Login
```
INFO - Login successful - IP: 192.168.1.100, Email: user@domain.com, UserID: 123, Role: ADMINISTRADOR
WARNING - Login failed - IP: 192.168.1.100, Email: user@domain.com, Reason: Invalid credentials or inactive user
ERROR - Login error - IP: 192.168.1.100, Email: user@domain.com, Error: Database connection failed
```

#### Patrones a Monitorear
- **Intentos fallidos consecutivos**: Posible ataque de fuerza bruta
- **IPs sospechosas**: Múltiples intentos desde misma IP
- **Usuarios inactivos**: Intentos de login de cuentas desactivadas

### 2. Servicios de IA

#### Eventos de Chatbot
```
INFO - Solicitud de chatbot recibida - Usuario: 123, Conversación: conv_456
INFO - Respuesta de chatbot generada exitosamente - Usuario: 123, Longitud: 250 caracteres
ERROR - Error al invocar el modelo de IA: Connection timeout
```

#### Eventos de Análisis
```
INFO - Iniciando análisis de sugerencias para reporte de incidente
INFO - Sugerencias de IA generadas exitosamente
WARNING - No se pudo enriquecer el incidente 123 por un error en el servicio de IA
```

#### Patrones a Monitorear
- **Tiempos de respuesta**: Latencia de llamadas a IA
- **Tasa de errores**: Fallos en servicios de IA
- **Uso por usuario**: Consumo de recursos de IA

### 3. Operaciones de Base de Datos

#### Eventos CRUD
```
INFO - Incident created - ID: 123, User: 456, Title: "Incidente de prueba"
INFO - Incident updated - ID: 123, User: 456, Fields: status, severity
WARNING - Database connection pool exhausted
```

## Configuración de Monitoreo

### Alertas Recomendadas

#### Seguridad
```yaml
# Intentos de login fallidos
- condition: rate(login_failed[5m]) > 10
  alert: "Alto número de logins fallidos"

# IPs sospechosas
- condition: count(login_attempts{ip=~".*"}[1h]) > 50
  alert: "Posible ataque de fuerza bruta desde IP"

# Usuarios inactivos
- condition: login_attempts{result="inactive_user"} > 5
  alert: "Múltiples intentos de usuarios inactivos"
```

#### Rendimiento
```yaml
# Respuesta lenta de IA
- condition: ai_response_time > 30s
  alert: "Servicio de IA lento"

# Errores de base de datos
- condition: rate(db_errors[5m]) > 5
  alert: "Alto número de errores de base de datos"

# Uso de CPU alto
- condition: cpu_usage > 85%
  alert: "Uso alto de CPU"
```

#### Disponibilidad
```yaml
# Servicio de IA no disponible
- condition: up{job="ai_service"} == 0
  alert: "Servicio de IA caído"

# Base de datos no disponible
- condition: up{job="database"} == 0
  alert: "Base de datos no disponible"
```

## Dashboard de Monitoreo

### Métricas Principales

#### Autenticación
- Total de logins por día
- Tasa de éxito de login (%)
- Intentos fallidos por IP
- Usuarios activos vs inactivos

#### Servicios de IA
- Número de consultas por hora
- Tiempo promedio de respuesta
- Tasa de error por servicio
- Uso de tokens de IA

#### Sistema General
- Uso de CPU y memoria
- Conexiones activas a BD
- Tiempos de respuesta de API
- Errores por endpoint

## Análisis de Logs

### Comandos Útiles

#### Backend
```bash
# Ver logs en tiempo real
docker logs -f fastapi_api

# Buscar errores específicos
docker logs fastapi_api | grep "ERROR"

# Filtrar por usuario
docker logs fastapi_api | grep "UserID: 123"

# Análisis de rendimiento
docker logs fastapi_api | grep "duration" | awk '{print $NF}' | sort -n
```

#### Frontend (en navegador)
```javascript
// Ver logs de la aplicación
console.log(localStorage.getItem('app_logs'));

// Filtrar logs por tipo
console.table(
  JSON.parse(localStorage.getItem('app_logs') || '[]')
  .filter(log => log.level === 'ERROR')
);
```

### Patrones de Búsqueda

#### Errores Comunes
```bash
# Errores de conexión
grep "connection" logs/app.log

# Errores de autenticación
grep "Login failed" logs/app.log

# Errores de IA
grep "IA\|AI" logs/app.log | grep "ERROR"
```

#### Análisis de Rendimiento
```bash
# Tiempos de respuesta promedio
grep "duration" logs/app.log | awk '{sum+=$2; count++} END {print sum/count}'

# Consultas más lentas
grep "duration" logs/app.log | sort -k2 -nr | head -10
```

## Resolución de Problemas

### Checklist de Troubleshooting

#### Problema: Login falla
1. ✅ Verificar configuración de BD
2. ✅ Revisar logs de autenticación
3. ✅ Verificar estado del usuario
4. ✅ Comprobar configuración de JWT

#### Problema: IA no responde
1. ✅ Verificar conectividad con proveedores de IA
2. ✅ Revisar configuración de API keys
3. ✅ Comprobar límites de rate limiting
4. ✅ Analizar logs de servicios de IA

#### Problema: Rendimiento lento
1. ✅ Monitorear uso de recursos
2. ✅ Revisar consultas a BD
3. ✅ Analizar logs de IA
4. ✅ Verificar configuración de caché

## Mejores Prácticas

### Logging
- ✅ Usar niveles apropiados (DEBUG, INFO, WARN, ERROR)
- ✅ Incluir contexto relevante (user_id, ip, timestamp)
- ✅ Evitar logging de información sensible
- ✅ Usar structured logging cuando sea posible

### Monitoreo
- ✅ Configurar alertas proactivas
- ✅ Monitorear métricas críticas
- ✅ Revisar logs regularmente
- ✅ Documentar incidentes y resoluciones

### Seguridad
- ✅ No loggear passwords o tokens
- ✅ Ofuscar información sensible en logs
- ✅ Monitorear accesos no autorizados
- ✅ Configurar rotación de logs

## Contactos de Soporte

- **Desarrollo**: Equipo de desarrollo
- **Infraestructura**: Equipo de DevOps
- **Seguridad**: Equipo de Ciberseguridad
- **Usuario Final**: Helpdesk

## Referencias

- [Documentación de FastAPI Logging](https://fastapi.tiangolo.com/tutorial/logging/)
- [Python Logging Best Practices](https://docs.python.org/3/howto/logging.html)
- [ELK Stack para centralización de logs](https://www.elastic.co/elk-stack)
- [Prometheus para métricas](https://prometheus.io/)