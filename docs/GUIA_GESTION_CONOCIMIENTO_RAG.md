# Guía de Gestión de Conocimiento para el Sistema RAG de ISIRT-IA

**Versión 2.0 (Actualizado tras mejoras de metadatos y JSON)**

## 1. Introducción: El Cerebro del Asistente de IA

Bienvenido a la guía de gestión de conocimiento para el Asistente de IA del sistema ISIRT. Este documento es la referencia central para todos los miembros del equipo de seguridad y administradores sobre cómo alimentar y mantener el "cerebro" de nuestro sistema de inteligencia artificial.

El Asistente de IA utiliza una técnica avanzada llamada **Generación Aumentada por Recuperación (RAG)**. El sistema no solo utiliza su conocimiento general, sino que "lee" y "entiende" los documentos que nosotros le proporcionamos. Esto le permite ofrecer análisis y recomendaciones alineadas con nuestras tecnologías, políticas y procedimientos internos.

El principio fundamental es simple:

> **La calidad y precisión de las recomendaciones de la IA dependen directamente de la calidad y actualización del conocimiento que le proporcionemos.**

## 2. ¿Qué Información Debemos Añadir? (Tipos de Conocimiento)

El sistema RAG puede procesar documentos en formato **PDF, Markdown (`.md`) y JSON (`.json`)**. Para maximizar su efectividad, debemos centrarnos en las siguientes categorías de conocimiento. Todos los documentos deben ser añadidos al directorio `playbooks/`.

### Tipos de Documentos Prioritarios:

| Prioridad | Tipo de Conocimiento | Descripción | Formato Recomendado |
| :--- | :--- | :--- | :--- |
| **Crítica** | **Playbooks de Respuesta a Incidentes** | Procedimientos detallados y paso a paso para gestionar tipos de incidentes específicos (phishing, ransomware, etc.). | Markdown (`.md`) |
| **Alta** | **Base de Conocimiento de MITRE ATT&CK** | El framework global de tácticas y técnicas de adversarios. Proporciona a la IA un contexto estandarizado sobre las acciones de los atacantes. | JSON (`.json`) |
| **Alta** | **Análisis Post-Incidente (Lecciones Aprendidas)** | Informes de incidentes pasados, detallando la causa raíz, las acciones tomadas y las lecciones aprendidas. | PDF o Markdown (`.md`) |
| **Media** | **Políticas y Procedimientos de Seguridad** | Las políticas oficiales de la organización sobre seguridad, respuesta a incidentes, clasificación de datos y comunicación. | PDF |
| **Media** | **Documentación Técnica y de Arquitectura** | Diagramas de red, inventarios de activos, guías de configuración segura para sistemas clave (firewalls, servidores, etc.). | PDF o Markdown (`.md`) |

## 3. Cómo Escribir Documentos Efectivos para la IA (Mejores Prácticas)

Para que la IA pueda "entender" un documento, no basta con que sea legible para un humano. Debe estar bien estructurado.

### 3.1. Convención de Nombres para Metadatos Automáticos

El sistema ahora es más inteligente y extrae metadatos directamente del nombre del archivo para realizar búsquedas filtradas. Es **crucial** seguir esta convención de nombres:

**Para Playbooks:** `playbook_{tipo-incidente}_{entorno}.md`
-   `{tipo-incidente}`: El tipo de amenaza. Ej: `phishing`, `ransomware`, `malware`.
-   `{entorno}`: El sistema principal al que aplica. Ej: `gworkspace`, `windows`, `linux`, `multios`.
-   **Ejemplos:**
    -   `playbook_phishing_gworkspace.md`
    -   `playbook_ransomware_multios.md`

**Para MITRE ATT&CK:** `enterprise-attack.json` (o similar)
-   El sistema identificará los archivos JSON que contengan "mitre" o "attack" en su nombre y les asignará el tipo de documento `mitre_attack`.

### 3.2. Principio de Atomicidad
Cada documento debe tratar sobre **un único tema y ser autocontenido**.
- **BIEN:** Un archivo `playbook_phishing.md` y otro `playbook_ransomware.md`.
- **MAL:** Un único archivo `todos_los_playbooks.md` con 20 tipos de incidentes.

### 3.3. Estructura y Formato con Markdown
El uso de la sintaxis de Markdown es **crucial**. La IA utiliza los títulos, subtítulos y listas para entender la jerarquía y la secuencia de la información. Utiliza siempre la plantilla estándar para Playbooks (se omite por brevedad, consultar versión anterior).

### 3.4. Lenguaje Claro y Palabras Clave
- **Sé directo y específico.** Usa frases accionables.
- **Incluye palabras clave importantes.** Menciona explícitamente nombres de **tecnologías, productos, servidores y códigos de error**. La IA usará estos términos para conectar el incidente actual con el documento correcto.
    - **BIEN:** "Revisar los logs del firewall **FortiGate 200F** para tráfico saliente anómalo en el puerto **TCP/3389**."
    - **MAL:** "Revisar los logs del firewall."

## 4. Proceso de Actualización del Conocimiento

Añadir nuevo conocimiento es un proceso de dos pasos:

1.  **Añadir el Documento:**
    - Crea tu documento (`.md`, `.pdf`, o `.json`) siguiendo las mejores prácticas.
    - Coloca el archivo en el directorio `playbooks/` del proyecto.

2.  **Re-indexar la Base de Conocimiento:**
    - Para que la IA "lea" el nuevo documento, debes actualizar su índice.
    - **Método Recomendado (Interfaz Web):**
        1.  Ve a la sección de **Administración -> Configuración del Modelo de IA**.
        2.  Haz clic en el botón **"Recargar Documentos RAG"**.
    - **Método Alternativo (Línea de Comandos):**
        - Ejecuta el siguiente comando desde la raíz de tu proyecto, usando el usuario `appuser`:
          ```bash
          docker compose exec -u appuser api python manage.py ingest-playbooks
          ```

## 5. Mantenimiento y Ciclo de Vida del Conocimiento

- **Revisión Periódica:** Agenda una revisión **trimestral** de todos los playbooks.
- **Versionado:** Mantén un historial de cambios en tus documentos.
- **Archivado de Conocimiento Obsoleto:** Elimina o archiva documentos obsoletos de la carpeta `playbooks/` y vuelve a re-indexar.

## 6. Solución de Problemas (Troubleshooting)

Durante la configuración y el mantenimiento, pueden surgir errores. Aquí están los más comunes y sus soluciones:

- **ERROR:** `No such command 'ingest_playbooks'`
    - **Causa:** La librería `Typer` convierte guiones bajos a guiones medios. El nombre del comando es incorrecto.
    - **Solución:** Usa el comando `ingest-playbooks` (con guion medio).

- **ERROR:** `jq package not found`
    - **Causa:** Falta la dependencia `jq` de Python, necesaria para procesar los archivos JSON.
    - **Solución:** Añade `jq==1.7.1` (o una versión reciente) a tu archivo `requirements.txt` y reconstruye la imagen de Docker (`docker compose build`).

- **ERROR:** `chown: ... Operation not permitted` o `could not open ... for writing: Permission denied`
    - **Causa:** Es un problema de permisos de Docker. El contenedor corre como `appuser`, pero los directorios montados como volúmenes (`logs`, `faiss_index`, `uploads`) son propiedad de `root`.
    - **Solución:** Asegúrate de que el `command` en tu `docker-compose.yml` para el servicio `api` asigne los permisos correctos en el arranque. Ejemplo:
      ```yaml
      command: sh -c "chown -R appuser:appuser /app/logs /app/faiss_index /app/uploads && su appuser -c 'uvicorn ...'"
      ```

- **ERROR:** `This account is not available` al usar `docker compose exec -u appuser ...`
    - **Causa:** El usuario `appuser` fue creado como un usuario de sistema sin una shell de inicio de sesión.
    - **Solución:** Modifica el `Dockerfile` para crear el usuario con una shell. Cambia `adduser -S` por `adduser -D -s /bin/sh` y reconstruye la imagen.

- **ERROR:** `429 You exceeded your current quota` durante la ingesta.
    - **Causa:** La ingesta de documentos (especialmente archivos grandes como el de MITRE) consume muchas llamadas a la API de embeddings (Gemini, OpenAI). Has superado el límite de tu plan.
    - **Solución:** Espera unos minutos y reintenta. Si el error persiste, revisa tu plan y facturación con el proveedor de la API o reduce la cantidad de documentos a ingestar.

---
*Este documento es una guía viva. Si descubres nuevas formas de mejorar la interacción con la IA, por favor, actualízala.*