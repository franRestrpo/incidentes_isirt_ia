# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2026-02-11

### Añadido
- Nueva interfaz de usuario profesional basada en React y Tailwind CSS.
- Sistema de Auditoría Avanzada con decoradores.
- Soporte para RAG con múltiples proveedores (Gemini, OpenAI, Ollama).
- Guía detallada de Despliegue y Troubleshooting.
- Licencia GPLv3.

### Cambiado
- Reestructuración de la documentación para un README más ligero.
- Mejora en la organización de los tests de rendimiento.
- Actualización de `docker-compose.yml` para mayor seguridad con variables genéricas.

### Seguridad
- Eliminación de secretos expuestos en archivos de configuración.
- Implementación de `.env.example` con marcadores de posición seguros.
