# 🛡️ Playbook de Respuesta a Incidentes de Ransomware: Asmet Salud EPS

**Versión:** 1.0
**Fecha:** 2025-10-01
**Clasificación:** Confidencial - Uso Interno

## 1. Introducción y Objetivos

Este playbook proporciona un marco de acción estructurado para que Asmet Salud EPS responda de manera eficaz y coordinada a un incidente de seguridad por **ransomware**. El objetivo principal es minimizar el impacto operativo, proteger la integridad y confidencialidad de los datos de los pacientes, asegurar la continuidad de los servicios de salud y cumplir con el marco regulatorio colombiano.

Este documento se alinea con el ciclo de vida de respuesta a incidentes del **NIST SP 800-61** y los controles de la norma **ISO 27001:2022**.

### 1.1. Alcance

Este plan aplica a toda la infraestructura tecnológica de Asmet Salud EPS, incluyendo sistemas on-premise y en la nube, que soportan operaciones críticas como la gestión de Historias Clínicas Electrónicas (HCE), sistemas de facturación, agendamiento (RIS), imagenología (PACS) y plataformas de telemedicina.

### 1.2. Roles y Responsabilidades (Matriz RACI)

El **Equipo de Respuesta a Incidentes de Seguridad (CSIRT)** lidera la ejecución de este playbook.

| Rol / Título | Tarea: Declarar Incidente | Tarea: Aislar Sistemas | Tarea: Comunicar a Directivos | Tarea: Restaurar desde Backups | Tarea: Notificar a Autoridades |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **CISO** | A | A | R | A | A |
| **Líder de Infraestructura** | R | R | I | R | C |
| **Oficial de Protección de Datos** | C | I | C | I | R |
| **Equipo de Soporte TI (N1/N2)**| I | R | I | I | I |
| **Gerencia General / Presidencia**| I | I | A | A | I |
| **Equipo Legal y de Cumplimiento**| C | C | R | C | R |

* **R:** Responsable (Ejecuta la tarea)
* **A:** Aprobador (Aprueba la acción)
* **C:** Consultado (Debe ser consultado)
* **I:** Informado (Debe ser informado)

---

## 2. Ciclo de Vida de la Respuesta a Incidentes (NIST)

### Fase 1: Preparación 🧐

[cite_start]La preparación es la base para una respuesta exitosa[cite: 52]. El objetivo es tener las herramientas, procesos y conocimientos listos *antes* de que ocurra un incidente.

**Checklist de Preparación:**

* **✅ Plan de Comunicación:** Plan de comunicación de crisis definido y probado (ver sección 3).
* **✅ Herramientas de Seguridad:**
    * [cite_start]EDR (Endpoint Detection and Response) y XDR desplegados y configurados en todos los endpoints y servidores[cite: 64, 77].
    * [cite_start]SIEM (Security Information and Event Management) configurado para correlacionar eventos y generar alertas tempranas[cite: 80].
    * [cite_start]Firewalls de red y WAF (Web Application Firewall) actualizados y auditados[cite: 64].
* **✅ Backups Inmutables (Regla 3-2-1):**
    * [cite_start]Se realizan copias de seguridad diarias de todos los datos críticos (HCE, bases de datos de afiliados)[cite: 60].
    * [cite_start]Las copias se almacenan en una bóveda inmutable y con *air-gap* (desconectada de la red principal)[cite: 61].
    * [cite_start]Se realizan simulacros de restauración trimestrales para validar la integridad de los backups[cite: 62].
* **✅ Concienciación y Capacitación:**
    * [cite_start]Campañas de formación mensuales para todos los colaboradores sobre identificación de phishing y ingeniería social[cite: 58].
    * Simulacros de phishing trimestrales para medir la efectividad de la capacitación.
* **✅ Gestión de Accesos:**
    * [cite_start]Principio de Mínimo Privilegio (Zero Trust) implementado en toda la organización[cite: 117].
    * [cite_start]Autenticación Multifactor (MFA) obligatoria para acceso a VPN, correo electrónico y sistemas críticos[cite: 80].
    * [cite_start]Deshabilitación de macros en documentos de Office provenientes de internet[cite: 118, 119].

---

### Fase 2: Detección y Análisis 🔍

[cite_start]El objetivo de esta fase es identificar un incidente lo antes posible, determinar su alcance y analizar su impacto[cite: 131, 132].

**Indicadores de Compromiso (IoCs) Comunes:**

* Archivos renombrados con extensiones desconocidas (ej: `.crypted`, `.locked`).
* Notas de rescate (`readme.txt`, `decrypt_instructions.html`) en múltiples directorios.
* Alertas del EDR/Antivirus sobre actividad de cifrado masivo.
* Picos inusuales de actividad de CPU o disco en servidores de archivos.
* [cite_start]Intentos de conexión saliente a direcciones IP sospechosas (C2 - Comando y Control)[cite: 159].
* Desactivación de herramientas de seguridad o servicios de backup.

**Flujo de Detección y Triage:**

```mermaid
graph TD
    A[Alerta de Seguridad o Reporte de Usuario] --> B{¿Es un indicador de ransomware?};
    B -- Sí --> C[Declarar Incidente Potencial - Activar CSIRT];
    B -- No --> D[Gestionar como evento de baja prioridad];
    C --> E[Analizar alcance: ¿Qué sistemas están afectados?];
    E --> F{¿Afecta sistemas críticos (HCE, PACS)?};
    F -- Sí --> G[Clasificar como Incidente CRÍTICO];
    F -- No --> H[Clasificar como Incidente ALTO];
    G --> I[Iniciar Fase de Contención INMEDIATAMENTE];
    H --> I;
```
___
### Fase 3: Contención, Erradicación y Recuperación 🛠️

Esta es la fase activa de respuesta, donde se aísla la amenaza, se elimina de la infraestructura y se restauran las operaciones.

#### **3.1 Contención**

El objetivo es evitar que el ransomware se propague.

**Acciones Inmediatas:**

1.  **Aislar los Sistemas Afectados:**
    * Desconectar físicamente de la red las estaciones de trabajo y servidores infectados.
    * Si no es posible, aislarlos lógicamente mediante VLANs o reglas de firewall.
2.  **Segmentar la Red:** Implementar reglas de firewall de emergencia para impedir la comunicación lateral (Este-Oeste), especialmente en el puerto SMB (445).
3.  **Preservar Evidencia:**
    * [cite_start]**No apagar los sistemas inmediatamente.** Tomar una imagen forense del disco y una captura de la memoria RAM de una muestra de equipos afectados. [cite: 158] Esto es crucial para el análisis posterior.
4.  [cite_start]**Identificar la Cepa del Ransomware:** Consultar con fuentes de inteligencia de amenazas (como MS-ISAC o proveedores de seguridad) para identificar la variante y buscar posibles descifradores públicos. [cite: 161, 163]
5.  [cite_start]**Revisar Logs:** Analizar logs de firewall, EDR, SIEM y Directorio Activo para identificar el punto de entrada, cuentas comprometidas y movimiento lateral. [cite: 197]

#### **3.2 Erradicación**

[cite_start]El objetivo es eliminar por completo la amenaza del entorno y mitigar las vulnerabilidades explotadas. [cite: 214, 215]

**Acciones Clave:**

1.  [cite_start]**Identificar y Eliminar la Causa Raíz:** Mitigar la vulnerabilidad que fue explotada para que no vuelva a ocurrir en el futuro. [cite: 217]
2.  **Reconstruir Sistemas Afectados:** **No intente "limpiar" los sistemas críticos.** La práctica recomendada es reconstruirlos desde una imagen dorada (plantilla segura y actualizada).
3.  **Restablecer Credenciales:** Forzar el cambio de contraseña de todas las cuentas de usuario y de servicio, priorizando las cuentas de administrador.

#### **3.3 Recuperación**

El objetivo es restaurar los datos y servicios de forma segura.

**Plan de Recuperación Priorizado:**

1.  [cite_start]**Verificar Entorno Limpio:** Asegurarse de que la red esté completamente libre del malware antes de iniciar la restauración para no reinfectar los sistemas. [cite: 221]
2.  [cite_start]**Restaurar Datos Críticos:** Restaurar las bases de datos de HCE, afiliados y facturación desde los backups inmutables y offline, priorizando los servicios más críticos. [cite: 220]
3.  **Restaurar Aplicaciones:** Levantar los servicios de atención al paciente en orden de criticidad (definido en el Plan de Continuidad de Negocio - BCP):
    * **Prioridad 1 (RTO < 4 horas):** Autenticación (Directorio Activo), HCE.
    * **Prioridad 2 (RTO < 12 horas):** Agendamiento, Facturación, LIS.
    * **Prioridad 3 (RTO < 24 horas):** PACS, Correo electrónico, Telemedicina.
4.  **Monitoreo Intensivo:** Vigilar de cerca la red y los sistemas restaurados en busca de cualquier actividad anómala.

**Decisión sobre el Pago del Rescate:**
La política de Asmet Salud EPS, alineada con las recomendaciones del Gobierno Nacional y las mejores prácticas internacionales, es **NO PAGAR EL RESCATE**. El pago no garantiza la recuperación de los datos, financia actividades criminales y convierte a la organización en un objetivo futuro.

---

### Fase 4: Actividades Post-Incidente (Lecciones Aprendidas) 📈

[cite_start]Esta fase es fundamental para mejorar la resiliencia de la organización. [cite: 237, 239]

**Acciones Post-Incidente:**

1.  **Reunión de Lecciones Aprendidas:** Dentro de las 2 semanas posteriores a la recuperación total, el CSIRT y las partes interesadas deben reunirse para analizar:
    * [cite_start]¿Qué funcionó bien? [cite: 237]
    * ¿Qué no funcionó? [cite_start]/ ¿Qué desafíos se enfrentaron? [cite: 237]
    * [cite_start]¿Cómo podemos mejorar nuestros procesos, herramientas y capacitación? [cite: 237]
2.  [cite_start]**Informe Final del Incidente:** Documentar una cronología detallada del incidente, el impacto, las acciones tomadas y las mejoras recomendadas. [cite: 238, 252, 255]
3.  **Actualización de Planes y Políticas:**
    * [cite_start]Refinar este playbook basándose en la experiencia real. [cite: 239]
    * [cite_start]Ajustar controles de seguridad, políticas y arquitecturas de red. [cite: 260]
4.  **Compartir Información (Controlado):**
    * [cite_start]Reportar los indicadores de compromiso (IoCs) de forma anónima al CSIRT del Gobierno Nacional para ayudar a proteger a otras entidades del sector. [cite: 235]

---

## 3. Protocolo de Comunicaciones

Una comunicación clara y oportuna es vital para gestionar la confianza y cumplir con las obligaciones legales.

| Audiencia | Canal de Comunicación | Responsable | Mensaje Clave |
| :--- | :--- | :--- | :--- |
| **Interno - CSIRT y Equipos Técnicos** | Canal seguro de Teams/Signal | CISO | Actualizaciones técnicas, asignación de tareas, estado del incidente. |
| **Interno - Comité Directivo** | Correo electrónico / Llamada directa | CISO / Gerente General | Resumen ejecutivo del impacto, estado de la recuperación, decisiones estratégicas. |
| **Interno - Todos los Colaboradores** | Correo masivo (desde un sistema seguro) | Gerencia General | Instrucciones claras (no usar equipos, no hablar con medios), estado general sin detalles técnicos. |
| **Externo - Superintendencia de Salud** | Oficio formal / Canal oficial | Oficial de Protección de Datos / Equipo Legal | Notificación del incidente de seguridad de datos personales, según lo exige la ley. |
| **Externo - Pacientes y Afiliados** | Comunicado oficial en sitio web / redes sociales | Equipo de Comunicaciones (aprobado por Gerencia) | Mensaje de transparencia sobre interrupción de servicios, sin confirmar detalles del ciberataque. Enfocado en soluciones y canales alternos de atención. |
| **Externo - Medios de Comunicación** | Vocero único designado (Gerente General) | Vocero designado | Comunicado de prensa oficial, controlado y alineado con la estrategia legal. |