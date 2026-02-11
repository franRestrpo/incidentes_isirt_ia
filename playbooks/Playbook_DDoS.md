# 🌊 Playbook de Respuesta a Incidentes DoS/DDoS: Asmet Salud EPS

**Versión:** 1.0
**Fecha:** 2025-10-01
**Clasificación:** Confidencial - Uso Interno

## 1. Introducción y Objetivos

Este playbook proporciona un marco de acción estructurado para que Asmet Salud EPS responda de manera eficaz y coordinada a un incidente de seguridad por **Denegación de Servicio (DoS/DDoS)**. El objetivo principal es garantizar la disponibilidad y el rendimiento de los servicios críticos de cara al público (HyL, sistema de agendamiento, Seven), minimizando el tiempo de interrupción y protegiendo la reputación de la entidad.

Este documento se alinea con el ciclo de vida de respuesta a incidentes del **NIST SP 800-61** y los controles de la norma **ISO 27001:2022**.

### 1.1. Alcance

Este plan aplica a toda la infraestructura y servicios expuestos a internet de Asmet Salud EPS, incluyendo sitios web, portales de afiliados y pacientes, APIs, servidores DNS y endpoints de VPN, que son los objetivos principales de los ataques DoS/DDoS.

### 1.2. Roles y Responsabilidades (Matriz RACI)

El **Equipo de Respuesta a Incidentes de Seguridad (CSIRT)**, en estrecha colaboración con el equipo de Redes y Operaciones (NOC/SOC), lidera la ejecución de este playbook.

| Rol / Título | Tarea: Declarar Incidente | Tarea: Activar Mitigación DDoS | Tarea: Comunicar a Directivos | Tarea: Contactar Proveedor/ISP | Tarea: Notificar a Autoridades |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **CISO** | A | A | R | A | A |
| **Líder de Infraestructura/Redes**| R | R | I | R | C |
| **Oficial de Protección de Datos** | C | I | C | I | R |
| **Equipo de Operaciones (SOC/NOC)**| I | R | I | R | I |
| **Gerencia General / Presidencia**| I | I | A | A | I |
| **Equipo Legal y de Cumplimiento**| C | I | R | C | R |

* **R:** Responsable (Ejecuta la tarea)
* **A:** Aprobador (Aprueba la acción)
* **C:** Consultado (Debe ser consultado)
* **I:** Informado (Debe ser informado)

---

## 2. Ciclo de Vida de la Respuesta a Incidentes (NIST)

### Fase 1: Preparación 🧐

La preparación es la defensa más efectiva contra un ataque DDoS. El objetivo es tener una arquitectura resiliente y los mecanismos de mitigación listos para ser activados.

**Checklist de Preparación:**

* **✅ Servicio de Mitigación DDoS:** Contratación y configuración de un servicio de mitigación DDoS (ej. Cloudflare, Akamai, AWS Shield) en modo "always-on" o con un plan de activación rápida (cambio de DNS).
* **✅ Arquitectura Resiliente:**
    * Balanceadores de carga distribuidos geográficamente.
    * Uso de una Red de Entrega de Contenidos (CDN) para distribuir el tráfico y absorber picos.
    * Infraestructura de servidores con capacidad de autoescalado.
* **✅ Línea Base de Tráfico:** Monitoreo y establecimiento de una línea base clara del tráfico de red normal (volumen, protocolos, origen) para poder identificar anomalías rápidamente.
* **✅ Contactos de Escalado:** Lista de contactos de emergencia (24x7) del proveedor de mitigación DDoS, el proveedor de servicios de internet (ISP) y el proveedor de hosting.
* **✅ Hardening de Red:**
    * Configuración de firewalls y routers para filtrar tráfico no deseado.
    * Implementación de listas de control de acceso (ACLs).

---

### Fase 2: Detección y Análisis 🔍

El objetivo es identificar un ataque en curso lo antes posible, diferenciarlo de un pico de tráfico legítimo y entender su naturaleza.

**Indicadores de Ataque Comunes:**

* Degradación severa o interrupción total del acceso a los portales web (errores 503 Service Unavailable).
* Latencia de red extremadamente alta para servicios externos.
* Alertas de monitoreo por saturación del ancho de banda de internet.
* Alertas de firewalls o balanceadores por alto consumo de CPU, memoria o tablas de estado.
* Un volumen masivo de tráfico proveniente de un gran número de direcciones IP geográficamente diversas (DDoS).
* Tráfico enfocado en un puerto o servicio específico (ej. DNS, HTTPS).

**Flujo de Detección y Triage:**

```mermaid
graph TD
    A[Alerta de Monitoreo o Reporte de Usuario sobre lentitud/caída] --> B{¿Corresponde a un pico masivo de tráfico anómalo?};
    B -- Sí --> C[Declarar Incidente Potencial - Activar CSIRT/NOC];
    B -- No --> D[Investigar como problema de rendimiento o falla de hardware];
    C --> E[Analizar vector: Volumétrico, Protocolo o Capa de Aplicación?];
    E --> F{¿Afecta servicios críticos de pacientes (portal, citas)?};
    F -- Sí --> G[Clasificar como Incidente CRÍTICO];
    F -- No --> H[Clasificar como Incidente ALTO];
    G --> I[Iniciar Fase de Mitigación INMEDIATAMENTE];
    H --> I;
```
____

### Fase 3: Contención, Mitigación (AWS WAF & Shield) y Recuperación 🛠️

El objetivo es utilizar las herramientas nativas de AWS para filtrar el tráfico malicioso de manera eficiente, restaurando la disponibilidad del servicio.

#### **3.1 Contención y Mitigación**

El objetivo es identificar el vector de ataque y aplicar las reglas de mitigación adecuadas en **AWS WAF** y confiar en la protección de **AWS Shield**.

**Acciones Inmediatas:**

1.  **Análisis y Diagnóstico en AWS:**
    * Revisar los dashboards de **Amazon CloudWatch** para identificar el pico de tráfico. Analizar métricas de ELB (Elastic Load Balancing), WAF y Shield.
    * Determinar el tipo de ataque:
        * **Ataque de Capa 7 (Aplicación):** Picos en `BlockedRequests` o `AllowedRequests` en AWS WAF, ataques a URLs específicas (ej. /login), HTTP Floods.
        * **Ataque de Capa 3/4 (Volumétrico):** Alertas de **AWS Shield**, saturación de ancho de banda a nivel de VPC.

2.  **Mitigación de Ataques de Capa 7 (AWS WAF):**
    * **Activar Rate-Based Rules:** Implementar o reducir el umbral de las reglas de limitación de tasa en **AWS WAF** para bloquear automáticamente las direcciones IP que excedan un número de peticiones en un corto período.
    * **Analizar Logs de WAF:** Usar **Amazon Athena** para consultar los logs de WAF en tiempo real. Identificar patrones en el tráfico de ataque (User-Agents, Referers, Geolocalización) y crear reglas personalizadas para bloquearlos.
    * **Desplegar AWS Managed Rules:** Asegurarse de que los grupos de reglas administradas por AWS (Ej: `Core rule set`, `Known bad inputs`) estén activos y en modo "Block".

3.  **Mitigación de Ataques de Capa 3/4 (AWS Shield):**
    * **Confiar en AWS Shield Standard:** Este servicio está activado por defecto y mitiga automáticamente el 96% de los ataques volumétricos comunes sin intervención.
    * **(Si se cuenta con él) Enganchar a la AWS DDoS Response Team (DRT):** Si la entidad tiene **AWS Shield Advanced**, abrir un caso de soporte de severidad "Crítico". El equipo de DRT de AWS se unirá para analizar el ataque y desplegar mitigaciones personalizadas y proactivas.

4.  **Ajuste de Network ACLs (NACLs):** Como medida de contención secundaria, si se identifican rangos de IP atacantes persistentes, se pueden bloquear a nivel de subred mediante las NACLs para reducir la carga en los recursos.

#### **3.2 Erradicación**

En este contexto, la "erradicación" es el proceso continuo de bloqueo y filtrado del tráfico malicioso. La tarea del equipo es monitorear la efectividad de las reglas en **AWS WAF** y los reportes de **AWS Shield**, ajustándolas según evolucione el ataque.

#### **3.3 Recuperación (Restauración del Servicio)**

El objetivo es verificar que los usuarios legítimos puedan acceder a los servicios una vez que las herramientas de AWS han mitigado el ataque.

**Plan de Restauración:**

1.  **Monitoreo de Métricas de AWS:** Observar en CloudWatch cómo las métricas de peticiones bloqueadas en WAF aumentan y las de los servidores (CPU, Conexiones) se estabilizan y regresan a la normalidad.
2.  **Validación de Servicios:** Realizar pruebas funcionales en los portales y APIs para asegurar que responden correctamente para el tráfico legítimo.
3.  **Ajuste Fino de Reglas WAF:** Una vez que el ataque cese, revisar y relajar gradualmente las reglas de "rate-limiting" más agresivas para evitar bloquear a usuarios legítimos (falsos positivos). Cambiar reglas de "Block" a "Count" para monitorear antes de desactivarlas.
4.  **Comunicar Restauración:** Informar a las partes interesadas internas que los servicios han vuelto a la normalidad.

---

### Fase 4: Actividades Post-Incidente (Lecciones Aprendidas) 📈

Esta fase es crucial para fortalecer la configuración de seguridad en AWS.

**Acciones Post-Incidente:**

1.  **Análisis del Reporte de AWS:**
    * Si se tiene **AWS Shield Advanced**, analizar en detalle el reporte post-incidente proporcionado por la DRT.
    * Revisar los logs completos de **AWS WAF** para documentar el vector exacto del ataque.
2.  **Reunión de Lecciones Aprendidas:** Convocar al CSIRT y al equipo de Cloud para evaluar:
    * ¿Fueron efectivas nuestras reglas preconfiguradas en WAF?
    * ¿Podríamos automatizar la creación de reglas dinámicas (ej. usando AWS Lambda)?
    * ¿El proceso para contactar a la DRT fue eficiente?
3.  **Afinar Configuraciones (Tuning) en AWS:**
    * Ajustar permanentemente las **rate-based rules** de AWS WAF basándose en el tráfico del ataque.
    * Crear nuevas reglas personalizadas para protegerse contra los patrones descubiertos.
    * Evaluar la implementación de **AWS Firewall Manager** para desplegar protecciones WAF de manera consistente en toda la organización.
4.  **Informe Ejecutivo:** Crear un informe final para la gerencia con el resumen del incidente, el impacto y, fundamentalmente, cómo la inversión en **AWS Shield Advanced** y la correcta configuración de **AWS WAF** minimizaron el tiempo de inactividad.

---

## 3. Protocolo de Comunicaciones

| Audiencia | Canal de Comunicación | Responsable | Mensaje Clave |
| :--- | :--- | :--- | :--- |
| **Interno - CSIRT y Equipo Cloud** | Canal seguro de Teams/Signal | CISO / Líder de Infraestructura | "Ataque DDoS en curso. Vector [X]. Mitigando con reglas en AWS WAF. Equipo de Shield Advanced contactado. Monitoreen CloudWatch." |
| **Interno - Comité Directivo** | Correo electrónico / Llamada directa | CISO | "Estamos bajo un ataque de denegación de servicio. Nuestras defensas en AWS están activas y mitigando el impacto. El acceso puede ser intermitente." |
| **Interno - Todos los Colaboradores** | Correo masivo / Intranet | Equipo de Comunicaciones | "Nuestros sistemas externos están presentando lentitud. Los equipos técnicos están trabajando para resolverlo. La operación interna no se ve afectada." |
| **Externo - Pacientes y Afiliados** | Comunicado en Redes Sociales (Twitter/Facebook) | Equipo de Comunicaciones | "Estamos experimentando dificultades técnicas en nuestro portal de pacientes. Apreciamos su paciencia mientras trabajamos para restaurar el servicio." |
| **Externo - AWS Support / DRT (Shield Advanced)** | Caso de Soporte (Severidad Crítica) | Líder de Infraestructura / NOC | "Declaramos un ataque DDoS contra nuestros recursos [IDs de recursos de AWS]. Solicitamos asistencia inmediata de la DDoS Response Team." |


___