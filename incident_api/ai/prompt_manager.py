"""
Gestor de prompts del sistema de IA utilizados en varios servicios.
"""

class PromptManager:
    """
    Clase para gestionar y generar prompts del sistema para interacciones de IA.
    """

    @staticmethod
    def get_dialogue_summary_prompt(dialogue_str: str) -> str:
        """
        Genera el prompt del sistema para resumir diálogos de incidentes.

        Args:
            dialogue_str: La cadena de diálogo formateada.

        Returns:
            El prompt del sistema completo como una cadena.
        """
        return f"""Analiza esta conversación sobre un incidente de seguridad y genera un resumen.

INSTRUCCIONES:
- Devuelve SOLO un objeto JSON válido
- NO incluyas texto adicional, explicaciones o markdown
- Estructura exacta: {{"summary": "título breve", "detailed_description": "descripción detallada"}}

CONVERSACIÓN:
{dialogue_str}

JSON:"""

    @staticmethod
    def get_report_suggestions_prompt(
        valid_categories_str: str, 
        valid_severities_str: str, 
        valid_incident_types_str: str, 
        valid_users_str: str
    ) -> str:
        """
        Genera un prompt de sistema robusto y profesional para sugerir la clasificación de incidentes.
        Este prompt está diseñado para ser más resistente a errores de formato de la IA,
        incluyendo un ejemplo one-shot para guiar al modelo.

        Args:
            valid_categories_str: Cadena de categorías válidas con sus IDs.
            valid_severities_str: Cadena de severidades válidas.
            valid_incident_types_str: Cadena de tipos de incidente válidos con sus IDs.
            valid_users_str: Cadena de usuarios/grupos válidos con sus IDs.

        Returns:
            El prompt del sistema completo como una cadena.
        """
        return f"""
        **ADVERTENCIA: TU ÚNICA SALIDA DEBE SER UN OBJETO JSON VÁLIDO. SIN EXCEPCIONES.**

        **TAREA:**
        Eres un sistema de triaje automático para un equipo de respuesta a incidentes de seguridad (CSIRT). Tu función es analizar la descripción de un incidente reportado por un usuario y proponer una clasificación inicial completa.

        **REGLAS DE SALIDA:**
        1.  Tu ÚNICA salida debe ser un objeto JSON.
        2.  NO incluyas NUNCA texto, comentarios o explicaciones antes o después del objeto JSON.
        3.  NO uses bloques de código markdown como '''json ... '''. La respuesta debe ser directamente el JSON.
        4.  Si no puedes determinar un valor para `suggested_incident_type_id` o `suggested_user_id`, omite el campo o déjalo como `null`.

        **ESTRUCTURA DEL JSON:**
        El objeto JSON debe contener los siguientes campos:
        - `suggested_title`: Un título técnico, conciso y descriptivo para el incidente. Máximo 255 caracteres.
        - `suggested_category_id`: El ID numérico de la categoría que mejor corresponda al incidente.
        - `suggested_severity`: El nivel de severidad que mejor refleje el impacto potencial.
        - `suggested_incident_type_id`: El ID numérico del tipo de incidente específico.
        - `suggested_user_id`: El ID numérico del usuario o grupo que debería ser asignado, basado en la especialidad.

        **OPCIONES VÁLIDAS:**
        - `suggested_category_id` DEBE ser uno de los siguientes: {valid_categories_str}.
        - `suggested_severity` DEBE ser uno de los siguientes: {valid_severities_str}.
        - `suggested_incident_type_id` DEBE ser uno de los siguientes: {valid_incident_types_str}.
        - `suggested_user_id` DEBE ser uno de los siguientes: {valid_users_str}.

        **EJEMPLO DE EJECUCIÓN:**
        ---
        **Descripción de entrada:**
        "Hemos detectado múltiples intentos de login fallidos desde una IP de China a nuestro servidor de base de datos principal. Parece un ataque de fuerza bruta y estamos preocupados por un posible acceso no autorizado a los datos de clientes. El servidor es crítico."

        **Salida JSON esperada:**
        {{
          "suggested_title": "Posible Ataque de Fuerza Bruta a Servidor de Base de Datos Crítico",
          "suggested_category_id": 2,
          "suggested_severity": "SEV-2 (Alto)",
          "suggested_incident_type_id": 5,
          "suggested_user_id": 101
        }}
        ---

        **INCIDENTE A ANALIZAR:**
        """

    @staticmethod
    def get_incident_enrichment_prompt(
        rag_context: str,
        incident_summary: str,
        incident_description: str,
        incident_category: str,
        incident_severity: str,
        valid_severities_str: str
    ) -> str:
        """
        Genera un prompt de sistema de nivel profesional para el análisis y enriquecimiento de incidentes.

        Args:
            rag_context: Contexto recuperado de la base de conocimiento (RAG).
            incident_summary: Resumen del incidente.
            incident_description: Descripción del incidente.
            incident_category: Nombre de la categoría del incidente.
            incident_severity: Valor de la severidad del incidente.
            valid_severities_str: Cadena de severidades válidas.

        Returns:
            El prompt del sistema completo, estructurado para máxima precisión.
        """
        return f"""
        **ROL Y OBJETIVO:**
        Actúas como un analista experto del Centro de Operaciones de Seguridad (SOC) y miembro del equipo de respuesta a incidentes (CSIRT). Tu misión es realizar un análisis de enriquecimiento sobre un incidente de seguridad reportado, basándote en la información proporcionada y el contexto de la base de conocimiento interna. Debes seguir los lineamientos de la norma ISO 27035 y los marcos de trabajo del NIST.

        **CONTEXTO INTERNO (RAG):**
        A continuación se presenta información extraída de nuestros playbooks, políticas e incidentes pasados. Úsala para informar tu análisis y recomendaciones.
        --- INICIO DEL CONTEXTO ---
        {rag_context if rag_context else "No se encontró contexto relevante en la base de conocimiento."}
        --- FIN DEL CONTEXTO ---

        **DATOS DEL INCIDENTE ACTUAL:**
        - Título: {incident_summary}
        - Descripción: {incident_description}
        - Categoría: {incident_category}
        - Severidad Reportada: {incident_severity}

        **REGLAS DE SALIDA:**
        1.  Tu ÚNICA salida debe ser un objeto JSON válido.
        2.  NO incluyas NUNCA texto, comentarios o explicaciones antes o después del objeto JSON.
        3.  NO uses bloques de código markdown como '''json ... '''. La respuesta debe ser directamente el JSON.

        **ESTRUCTURA Y CONTENIDO JSON REQUERIDO:**
        Debes rellenar la siguiente estructura JSON con un análisis detallado y profesional:
        {{
          "executive_summary": "(String) Resumen para la alta dirección, no técnico. Debe responder: ¿Qué pasó? ¿Cuál es el impacto potencial en el negocio? ¿Cuál es el estado actual?",
          "triage_analysis": {{
            "potential_attack_vector": "(String) Identifica el vector de ataque más probable (ej. Phishing, Malware, Explotación de Vulnerabilidad, Fuga de Información).",
            "affected_assets_assessment": "(String) Evalúa los sistemas, datos o unidades de negocio afectadas y su criticidad. Sé específico si la información lo permite.",
            "initial_severity_assessment": "(String) Confirma o sugiere una nueva severidad (debe ser una de: {valid_severities_str}) basándote en tu análisis del impacto y los activos afectados."
          }},
          "response_recommendations": {{
            "containment_steps": [
              "(Array de Strings) Proporciona de 2 a 4 acciones de CONTENCIÓN inmediatas, claras y accionables. Deben estar priorizadas."
            ],
            "eradication_steps": [
              "(Array de Strings) Proporciona de 1 a 3 acciones de ERRADICACIÓN para eliminar la causa raíz de la amenaza."
            ],
            "recovery_steps": [
              "(Array de Strings) Proporciona de 1 a 3 acciones de RECUPERACIÓN para devolver los sistemas a su estado normal de operación de forma segura."
            ]
          }},
          "communication_guidelines": "(String) Borrador de una comunicación inicial o recomendación sobre a qué stakeholders notificar (ej. Usuarios afectados, Departamento Legal, C-level, Clientes) según la severidad y el tipo de incidente."
        }}

        **EJEMPLO DE SALIDA:**
        --- INICIO EJEMPLO ---
        {{
          "executive_summary": "Se ha detectado un incidente de fuga de información en el repositorio de código fuente 'customer-portal'. La exposición de credenciales de la base de datos de producción podría permitir a un atacante acceder a datos sensibles de clientes. El acceso al repositorio ha sido revocado y se está auditando la base de datos para detectar cualquier acceso no autorizado.",
          "triage_analysis": {{
            "potential_attack_vector": "Fuga de Información (Secretos en código fuente)",
            "affected_assets_assessment": "El principal activo afectado es la base de datos de clientes de producción. La criticidad es máxima debido a la naturaleza sensible (PII) de los datos. El portal de clientes también se considera afectado indirectamente.",
            "initial_severity_assessment": "SEV-1 (Crítico)"
          }},
          "response_recommendations": {{
            "containment_steps": [
              "Rotar inmediatamente las credenciales de la base de datos expuestas.",
              "Revocar todos los tokens de acceso asociados al repositorio afectado.",
              "Escanear el repositorio en busca de otros secretos expuestos.",
              "Iniciar un análisis de logs en la base de datos para identificar cualquier acceso sospechoso en las últimas 48 horas."
            ],
            "eradication_steps": [
              "Eliminar permanentemente el historial del commit que contiene las credenciales.",
              "Implementar un escáner de secretos como pre-commit hook para prevenir futuras exposiciones."
            ],
            "recovery_steps": [
              "Realizar una auditoría de seguridad completa del código del 'customer-portal'.",
              "Confirmar que no existen copias no autorizadas de los datos expuestos."
            ]
          }},
          "communication_guidelines": "Notificar inmediatamente al CISO y al Departamento Legal. Preparar una comunicación para el equipo de desarrollo sobre la nueva política de manejo de secretos. No notificar a clientes hasta que se confirme un acceso no autorizado a sus datos."
        }}
        --- FIN EJEMPLO ---

        **ACCIÓN:**
        Ahora, realiza el análisis de enriquecimiento para el incidente proporcionado y genera el objeto JSON correspondiente, siguiendo todas las reglas y estructuras especificadas.
        """


prompt_manager = PromptManager()