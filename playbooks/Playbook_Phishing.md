# 🎣 Playbook de Respuesta a Incidentes de Phishing: Asmet Salud EPS

**Versión:** 1.0
**Fecha:** 2025-10-01
**Clasificación:** Confidencial - Uso Interno

## 1. Introducción y Objetivos

Este playbook proporciona un marco de acción estructurado para que Asmet Salud EPS identifique, contenga y responda eficazmente a los incidentes de **phishing**. El objetivo principal es prevenir el compromiso de credenciales, la instalación de malware y la exfiltración de datos sensibles (como Historias Clínicas Electrónicas), protegiendo así la integridad de nuestros sistemas y la confianza de nuestros afiliados.

Este documento se alinea con el ciclo de vida de respuesta a incidentes del **NIST SP 800-61** y los controles de la norma **ISO 27001:2022**.

### 1.1. Alcance

Este plan aplica a todos los colaboradores (empleados y contratistas) de Asmet Salud EPS y cubre todos los vectores de phishing, incluyendo correo electrónico (phishing), mensajes de texto (smishing) y llamadas de voz (vishing).

### 1.2. Roles y Responsabilidades (Matriz RACI)

El **Equipo de Respuesta a Incidentes de Seguridad (CSIRT)**, en conjunto con el equipo de TI y la Mesa de Ayuda, lidera la ejecución de este playbook.

| Rol / Título | Tarea: Declarar Incidente | Tarea: Analizar Correo Malicioso | Tarea: Bloquear Remitente/URL | Tarea: Resetear Credenciales Comprometidas | Tarea: Comunicar a Usuarios Afectados |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **CISO** | A | A | A | A | A |
| **Analista de Seguridad (SOC)**| R | R | C | I | C |
| **Administrador de Correo/Seguridad TI**| I | C | R | R | I |
| **Mesa de Ayuda (Help Desk)**| I | I | I | R | R |
| **Gerencia General / Presidencia**| I | I | I | I | I |
| **Equipo de Comunicaciones**| C | I | I | I | R |

* **R:** Responsable (Ejecuta la tarea)
* **A:** Aprobador (Aprueba la acción)
* **C:** Consultado (Debe ser consultado)
* **I:** Informado (Debe ser informado)

---

## 2. Ciclo de Vida de la Respuesta a Incidentes (NIST)

### Fase 1: Preparación 🧐

La preparación se centra en defensas técnicas robustas y, fundamentalmente, en un colaborador bien entrenado.

**Checklist de Preparación:**

* **✅ Defensas de Correo Electrónico:**
    * Implementación y configuración en modo "reject" de **SPF, DKIM y DMARC**.
    * Uso de un **Gateway de Correo Seguro (SEG)** con capacidades anti-phishing, anti-malware y sandboxing de archivos adjuntos.
    * Habilitación de la reescritura y análisis de URLs en tiempo real (**Safe Links**).
* **✅ Concienciación y Capacitación:**
    * Programa de formación en ciberseguridad obligatorio y continuo para todos los colaboradores.
    * **Simulacros de phishing trimestrales** para medir la efectividad y reforzar el aprendizaje.
* **✅ Herramienta de Reporte Fácil:**
    * Implementación de un **botón "Reportar Phishing"** en el cliente de correo (Outlook/Gmail) que envíe automáticamente el correo sospechoso a una bandeja de análisis de seguridad.
* **✅ Gestión de Identidad:**
    * **Autenticación Multifactor (MFA)** obligatoria para todos los accesos a sistemas críticos, VPN y correo electrónico.

---

### Fase 2: Detección y Análisis 🔍

El objetivo es analizar rápidamente los correos reportados para confirmar si son maliciosos y evaluar el alcance inicial del ataque.

**Indicadores de Ataque Comunes:**

* Reportes de usuarios a través del botón "Reportar Phishing".
* Alertas del Gateway de Correo Seguro sobre una campaña de phishing bloqueada.
* Múltiples reportes de usuarios sobre un correo electrónico similar.
* Detección de logins anómalos (ej. desde geografías inusuales) en las cuentas de los usuarios.
* Alertas de MFA por intentos de acceso no autorizados.

**Flujo de Detección y Triage:**

```mermaid
graph TD
    A[Reporte de Usuario o Alerta de Gateway] --> B{¿El correo es malicioso? (Analizar en Sandbox)};
    B -- Sí --> C[Declarar Incidente de Phishing - Activar CSIRT];
    B -- No --> D[Cerrar caso y notificar al usuario (Falso Positivo)];
    C --> E[Análisis de Impacto: ¿Quién más lo recibió? ¿Hay evidencia de clics o compromiso de credenciales?];
    E --> F{¿Credenciales Comprometidas o Malware instalado?};
    F -- Sí --> G[Clasificar como Incidente CRÍTICO];
    F -- No --> H[Clasificar como Incidente MEDIO];
    G --> I[Iniciar Fase de Contención INMEDIATAMENTE];
    H --> I;
```
___

### Fase 3: Contención, Erradicación y Recuperación 🛠️

Esta fase se enfoca en neutralizar la amenaza y remediar cualquier compromiso de cuentas o sistemas.

#### **3.1 Contención**

El objetivo es evitar que otros usuarios interactúen con la amenaza.

**Acciones Inmediatas:**

1.  **Búsqueda y Eliminación:** Utilizar las herramientas de administración del servidor de correo para buscar todos los correos electrónicos idénticos o similares (por remitente, asunto, etc.) en todos los buzones y moverlos a cuarentena.
2.  **Bloqueo de Indicadores (IOCs):**
    * Bloquear el dominio o la dirección IP del remitente en el Gateway de Correo Seguro.
    * Bloquear las URLs maliciosas en el proxy web, el DNS corporativo y la solución de EDR.
    * Si hay un archivo adjunto malicioso, bloquear su hash (MD5, SHA256) en la solución de EDR/Antivirus.

#### **3.2 Erradicación**

El objetivo es eliminar el punto de apoyo que el atacante haya podido obtener.

**Acciones Clave:**

1.  **Compromiso de Credenciales:**
    * **Inmediatamente forzar el cierre de todas las sesiones activas** del usuario afectado.
    * **Forzar un reseteo de contraseña inmediato.** El usuario no podrá volver a usar la misma contraseña.
    * Revisar la cuenta en busca de actividad maliciosa (ej. creación de reglas de reenvío, envío de correos, acceso a archivos).
2.  **Instalación de Malware:**
    * **Aislar de la red el equipo afectado** de forma inmediata.
    * Proceder con el playbook específico de respuesta a incidentes de malware (análisis forense, reimagen del equipo).

#### **3.3 Recuperación**

El objetivo es devolver al usuario y/o sistema a un estado operativo seguro.

**Plan de Recuperación:**

1.  **Restauración de Cuenta:** Una vez que la contraseña ha sido cambiada y las sesiones revocadas, el equipo de Mesa de Ayuda asiste al usuario para que recupere el acceso seguro a su cuenta.
2.  **Restauración de Equipo:** Si el equipo fue aislado por malware, se restaura a partir de una imagen limpia y corporativa.
3.  **Comunicación Directa:** Contactar al usuario afectado para explicarle lo sucedido, confirmar que el acceso ha sido restaurado y ofrecerle una micro-capacitación de refuerzo.
4.  **Liberación de Falsos Positivos:** Si algún correo legítimo fue puesto en cuarentena durante la contención, liberarlo al buzón del usuario.

---

### Fase 4: Actividades Post-Incidente (Lecciones Aprendidas) 📈

Esta fase es vital para mejorar la postura de seguridad y la resiliencia de la organización.

**Acciones Post-Incidente:**

1.  **Documentación del Incidente:** Registrar todos los detalles de la campaña de phishing (vector, remitente, asunto, URLs, etc.) en el sistema de gestión de incidentes.
2.  **Análisis de Causa Raíz:** Determinar por qué el correo de phishing no fue bloqueado por las defensas automáticas. ¿Era una técnica novedosa? ¿Un error de configuración?
3.  **Afinar Controles de Seguridad (Tuning):**
    * Ajustar las reglas del Gateway de Correo Seguro para mejorar la detección.
    * Añadir los nuevos IOCs a las listas de bloqueo permanentes.
4.  **Reforzar la Concienciación:** Utilizar el ejemplo del ataque (de forma anónima) como material didáctico en la próxima campaña de comunicación o simulación de phishing para mostrar un caso real.

---

## 3. Protocolo de Comunicaciones

La comunicación debe ser rápida, clara y dirigida a las audiencias correctas.

| Audiencia | Canal de Comunicación | Responsable | Mensaje Clave |
| :--- | :--- | :--- | :--- |
| **Interno - CSIRT y Equipos TI** | Canal seguro de Teams/Signal | CISO / Analista de Seguridad | "Campaña de phishing detectada. IOCs adjuntos. Procediendo a buscar y destruir. Investigando posible compromiso de credenciales." |
| **Interno - Mesa de Ayuda** | Correo electrónico / Chat | Analista de Seguridad | "Atención: estamos manejando un incidente de phishing. Estén preparados para asistir a usuarios con reseteo de contraseñas. Notificar al CSIRT si los usuarios reportan actividad extraña." |
| **Interno - Usuario(s) Afectado(s)** | Llamada directa / Correo de notificación | Mesa de Ayuda / Comunicaciones | "Detectamos una interacción con un correo malicioso desde tu cuenta. Para protegerte, hemos reseteado tu contraseña. Por favor, contacta a la Mesa de Ayuda para restablecer tu acceso." |
| **Interno - Todos los Colaboradores (si la campaña es masiva)** | Correo masivo / Intranet | Equipo de Comunicaciones | "Alerta de Seguridad: Se ha detectado una campaña de correos maliciosos. Por favor, no abran correos sospechosos y repórtenlos usando el botón 'Reportar Phishing'. El equipo de seguridad está gestionando la situación." |

___
