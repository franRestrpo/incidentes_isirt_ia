"""
Servicio para la lógica de negocio relacionada con el análisis de incidentes por IA.
"""

import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException
from langchain_core.messages import SystemMessage, HumanMessage

from incident_api import crud, schemas, models
from incident_api.models.incident import IncidentSeverity
from incident_api.services.llm_service import llm_service
from incident_api.services.rag_retrieval_service import rag_retrieval_service
from incident_api.services.ai_text_utils import sanitize_for_prompt
from incident_api.ai.prompt_manager import prompt_manager
from incident_api.schemas.ai_analysis import (
    TriageAnalysis,
    ResponseRecommendations,
    IncidentEnrichmentResponse
)

logger = logging.getLogger(__name__)

class IncidentAnalysisService:
    """
    Clase de servicio para gestionar la lógica de negocio de análisis de incidentes.
    """

    async def get_report_suggestions(
        self,
        db: Session,
        description: str,
        settings: models.AIModelSettings
    ) -> schemas.IncidentSuggestionResponse:
        """
        Analiza la descripción de un incidente y sugiere título, categoría, severidad, tipo y responsable.
        """
        logger.info("Iniciando análisis de sugerencias para reporte de incidente")
        logger.debug(f"Descripción del incidente: {description[:100]}...")

        # Obtener datos para las opciones del prompt
        categories = crud.incident_category.get_multi(db)
        incident_types = crud.incident_type.get_multi(db)
        users = crud.user.get_multi(db)
        groups = crud.group.get_multi(db)
        logger.debug(f"{len(categories)} categorías, {len(incident_types)} tipos, {len(users)} usuarios, {len(groups)} grupos encontrados.")

        # Formatear las opciones para el prompt
        valid_categories_str = ", ".join([
            f"'{sanitize_for_prompt(cat.name)}' (ID: {cat.incident_category_id})" for cat in categories
        ])
        valid_severities_str = ", ".join([f"'{s.value}'" for s in IncidentSeverity])
        valid_incident_types_str = ", ".join([
            f"'{sanitize_for_prompt(it.name)}' (ID: {it.incident_type_id})" for it in incident_types
        ])
        
        user_options = [f"'{sanitize_for_prompt(user.full_name)}' (ID: {user.user_id})" for user in users]
        group_options = [f"'{sanitize_for_prompt(group.name)}' (ID: {group.id})" for group in groups]
        valid_users_str = ", ".join(user_options + group_options)

        system_prompt = prompt_manager.get_report_suggestions_prompt(
            valid_categories_str, 
            valid_severities_str, 
            valid_incident_types_str, 
            valid_users_str
        )

        final_prompt = f"{system_prompt}{sanitize_for_prompt(description)}\n\nJSON:"

        messages = [
            SystemMessage(content=final_prompt),
        ]

        ai_suggestions_dict = await llm_service.invoke_for_json(messages, settings)
        logger.info("Sugerencias de IA generadas exitosamente")
        logger.debug(f"Sugerencias generadas: {ai_suggestions_dict}")
        return schemas.IncidentSuggestionResponse(**ai_suggestions_dict)

    def get_incident_context_for_rag(self, incident: models.Incident) -> str:
        """
        Construye una consulta enriquecida para el RAG a partir de un incidente.
        """
        # Prioriza la información más relevante para la búsqueda de similitud
        context = f"""
        Título del Incidente: {incident.summary}
        Categoría: {incident.incident_category.name if incident.incident_category else 'N/A'}
        Severidad: {incident.severity.value if incident.severity else 'N/A'}
        Descripción: {incident.description}
        """
        return context.strip()

    async def get_incident_enrichment(
        self,
        db: Session,
        incident: models.Incident,
        settings: models.AIModelSettings
    ) -> dict:
        """
        Analiza un incidente completo con contexto RAG y genera un análisis enriquecido,
        incluyendo trazabilidad y nivel de confianza.
        """
        logger.info(f"Iniciando enriquecimiento para el incidente ID: {incident.incident_id}")
        enriched_prompt = self.get_incident_context_for_rag(incident)
        
        # 1. Obtener contexto RAG con scores y filtrado por curación
        retrieved_items = await rag_retrieval_service.retrieve_context(db, enriched_prompt)
        
        rag_context = "\n".join([item["doc"].page_content for item in retrieved_items])
        scores = [item["score"] for item in retrieved_items]
        
        # 2. Calcular Nivel de Confianza
        avg_score = sum(scores) / len(scores) if scores else 0
        if avg_score > 0.75:
            confidence_level = "Alta"
        elif avg_score > 0.6:
            confidence_level = "Media"
        else:
            confidence_level = "Baja"

        # 3. Construir los fragmentos de fuente para la trazabilidad
        source_fragments = [
            schemas.SourceFragment(
                source_name=item["doc"].metadata.get("source_name", "Desconocido"),
                source_version=item["doc"].metadata.get("source_version", "N/A"),
                content=item["doc"].page_content,
                confidence_score=item["score"]
            ) for item in retrieved_items
        ]

        # 4. Generar el análisis del LLM
        valid_severities_str = ", ".join([s.value for s in IncidentSeverity])
        system_prompt = prompt_manager.get_incident_enrichment_prompt(
            sanitize_for_prompt(rag_context) if rag_context else "",
            sanitize_for_prompt(incident.summary),
            sanitize_for_prompt(incident.description),
            sanitize_for_prompt(incident.incident_category.name if incident.incident_category else 'N/A'),
            sanitize_for_prompt(incident.severity.value if incident.severity else 'N/A'),
            valid_severities_str
        )

        messages = [SystemMessage(content=system_prompt)]

        try:
            enrichment_dict = await llm_service.invoke_for_json(messages, settings)
            enrichment_response = IncidentEnrichmentResponse(**enrichment_dict)
            logger.info(f"Enriquecimiento de incidente {incident.incident_id} generado exitosamente.")

            # 5. Combinar todo en una única respuesta
            final_response = {
                "enrichment": enrichment_response.dict(),
                "rag_suggestion": schemas.RAGSuggestion(
                    suggestion_text=enrichment_response.executive_summary, # Usar el resumen como texto principal
                    confidence_level=confidence_level,
                    sources=source_fragments
                ).dict()
            }
            return final_response

        except HTTPException:
            logger.warning(f"No se pudo enriquecer el incidente {incident.incident_id} por un error en el servicio de IA.")
            return {}
        except Exception as e:
            logger.error(f"Error al procesar la respuesta de enriquecimiento para el incidente {incident.incident_id}: {e}", exc_info=True)
            return {}

incident_analysis_service = IncidentAnalysisService()
