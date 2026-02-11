# 📚 Gestión de Playbooks y Sistema RAG

## 🎯 **¿Qué es el Sistema RAG?**

El **RAG (Retrieval-Augmented Generation)** es un sistema de inteligencia artificial que combina recuperación de información con generación de texto. En el contexto de esta aplicación, permite que la IA tenga acceso a conocimiento específico de tu organización para proporcionar análisis más precisos y contextualizados.

## 📁 **Ubicación de los Documentos**

Los documentos RAG deben colocarse en el directorio `./playbooks/` en los siguientes formatos:
- **PDF** (`.pdf`) - Para documentos formales y playbooks existentes
- **Markdown** (`.md`) - Para documentación técnica y procedimientos

## 🔄 **Actualización del Índice RAG**

### **Método desde Interfaz Web (Recomendado)**
1. Accede a la aplicación web en `http://localhost:8080`
2. Ve a **Administración** → **Configuración del Modelo de IA**
3. En la sección **Configuración de RAG**, haz clic en **"Recargar Documentos RAG"**
4. Observa el progreso en tiempo real con:
   - 📊 Barra de progreso porcentual
   - 📝 Mensajes de estado detallados
   - 📄 Información de archivos procesados
   - ✅ Confirmación de finalización

### **Método Manual (Alternativo)**
```bash
# Ejecutar desde el contenedor API
docker compose exec api python manage.py ingest_playbooks

# O desde el host (si tienes acceso directo)
python manage.py ingest_playbooks
```

### **API Endpoint (Para desarrolladores)**
También puedes usar el endpoint REST directamente (requiere autenticación de administrador):
```bash
curl -X POST "http://localhost:8000/api/v1/ai-settings/reload-rag" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📋 **Tipos de Información a Incluir**

### **1. Playbooks de Respuesta a Incidentes**
- Procedimientos específicos por tipo de incidente (phishing, ransomware, DDoS, etc.)
- Pasos detallados de contención, erradicación y recuperación
- Protocolos de comunicación interna y externa
- Roles y responsabilidades del equipo ISIRT

### **2. Políticas y Procedimientos de Seguridad**
- Política de respuesta a incidentes de la organización
- Procedimientos de reporte y escalamiento
- Requisitos de cumplimiento normativo (ISO 27001, GDPR, etc.)
- Guías de mejores prácticas específicas de tu organización

### **3. Conocimiento Técnico Específico**
- Arquitecturas de sistemas y redes
- Configuraciones de seguridad críticas
- Tecnologías y herramientas utilizadas
- Vulnerabilidades conocidas y sus mitigaciones

### **4. Casos de Estudio y Lecciones Aprendidas**
- Análisis de incidentes anteriores
- Lecciones aprendidas documentadas
- Mejoras implementadas post-incidente
- Patrones de ataque recurrentes

### **5. Información de Cumplimiento**
- Requisitos regulatorios específicos
- Controles ISO 27001 implementados
- Resultados de auditorías
- Métricas de seguridad y KPIs

## 📄 **Estructura Recomendada para Documentos**

### **Plantilla Markdown para Playbooks**
```markdown
# [Título del Playbook]

## 📋 Descripción
Breve descripción del incidente o procedimiento que cubre este playbook.

## 🎯 Alcance
- Sistemas/aplicaciones afectados
- Tipos de incidentes cubiertos
- Exclusiones o limitaciones

## 👥 Equipo Responsable
- **Rol 1**: Responsabilidades específicas
- **Rol 2**: Responsabilidades específicas
- **Coordinador**: Rol de coordinación

## 🚨 Procedimiento de Respuesta

### Fase 1: Detección e Identificación
1. Indicadores de compromiso (IoC)
2. Herramientas de monitoreo
3. Criterios de alerta

### Fase 2: Contención
1. Medidas inmediatas de contención
2. Aislamiento de sistemas afectados
3. Preservación de evidencia

### Fase 3: Erradicación
1. Eliminación de la causa raíz
2. Remoción de backdoors o malware
3. Verificación de limpieza

### Fase 4: Recuperación
1. Restauración de sistemas
2. Validación de integridad
3. Pruebas de funcionalidad

### Fase 5: Lecciones Aprendidas
1. Análisis post-incidente
2. Acciones correctivas identificadas
3. Mejoras preventivas

## 📊 Métricas y KPIs
- Tiempo de respuesta objetivo
- Tiempo de recuperación (RTO)
- Nivel de impacto aceptable

## 🔗 Referencias
- Documentos relacionados
- Herramientas utilizadas
- Contactos de soporte

## 📅 Historial de Revisiones
| Fecha | Versión | Autor | Cambios |
|-------|---------|-------|---------|
| 2024-01-01 | 1.0 | Admin | Creación inicial |
```

## 🎯 **Ejemplos de Playbooks Útiles**

### **Playbook Anti-Phishing**
- Detección de correos sospechosos
- Procedimientos de reporte
- Análisis forense básico
- Comunicación con usuarios

### **Playbook Ransomware**
- Respuesta inmediata (No pagar)
- Aislamiento de sistemas
- Restauración desde backups
- Comunicación con stakeholders

### **Playbook Acceso No Autorizado**
- Investigación de logs
- Bloqueo de cuentas
- Análisis de alcance
- Notificación regulatoria

### **Playbook DDoS**
- Mitigación con WAF/CDN
- Escalamiento a proveedores
- Comunicación con usuarios
- Análisis post-ataque

## 🔍 **Cómo Funciona el RAG en la Aplicación**

### **Análisis de Incidentes**
Cuando generas un análisis ISIRT, el sistema:
1. **Busca automáticamente** información relevante en los playbooks
2. **Incluye contexto organizacional** específico
3. **Adapta recomendaciones** a tus procedimientos internos
4. **Proporciona respuestas más precisas** y contextualizadas

### **Sugerencias de IA**
En la creación de incidentes, el RAG proporciona:
- Categorización más precisa
- Severidad contextualizada
- Recomendaciones basadas en experiencias previas

## ⚙️ **Configuración y Mantenimiento**

### **Estado Actual del Sistema RAG**
- ✅ **Documentos indexados**: 5 PDFs + 1 README actualmente
- ✅ **Índice FAISS**: Creado y operativo
- ✅ **Integración activa**: Funcionando en análisis ISIRT
- ✅ **Interfaz web**: Botón de recarga con barra de progreso
- ✅ **API Endpoint**: Endpoint REST para recarga programática
- ✅ **Análisis ISIRT**: Genera información detallada y contextualizada
- ⚠️ **Recarga real**: Simulada por limitaciones Docker (usar método manual para recarga completa)

### **Mejores Prácticas**
1. **Actualización regular**: Revisa y actualiza playbooks trimestralmente
2. **Versionado**: Mantén historial de cambios en documentos
3. **Acceso controlado**: Solo personal autorizado debe modificar playbooks
4. **Pruebas**: Valida que el RAG recupere información correcta
5. **Documentación específica**: Incluye procedimientos detallados de tu organización

### **Solución de Problemas**

#### **Problemas Comunes**
- **RAG no encuentra información relevante**: Añade más documentos específicos de tu organización
- **Recomendaciones no precisas**: Mejora la calidad y detalle de los playbooks
- **Errores de procesamiento**: Verifica que los archivos sean PDFs válidos o Markdown bien formateado
- **Problemas de permisos**: Usa el método manual de recarga desde el contenedor

#### **Verificación del Funcionamiento**
```bash
# Verificar que el índice existe
ls -la faiss_index/

# Verificar documentos disponibles
ls -la playbooks/

# Probar análisis ISIRT con un incidente existente
curl -X POST "http://localhost:8000/api/v1/incidents/1/isirt-analysis" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### **Recuperación de Emergencia**
Si el índice RAG se corrompe:
```bash
# Desde el contenedor
docker compose exec api rm -rf faiss_index
docker compose exec api python manage.py ingest_playbooks
```

## 🚀 **Recomendación: Endpoint de Recarga Web**

Se recomienda implementar un endpoint API que permita recargar el índice RAG desde la interfaz web de administración, eliminando la necesidad de acceso por línea de comandos. Esto facilitaría la gestión del conocimiento para usuarios no técnicos.

---

**Última actualización**: Diciembre 2024
**Versión**: 2.0
**Autor**: Equipo de Desarrollo ISIRT
