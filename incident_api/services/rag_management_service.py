"""
Servicio para la gestión y recarga de documentos RAG.
"""

import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
import asyncio
from typing import Dict, Any

from incident_api.ai.rag_processor import RAGProcessor

logger = logging.getLogger(__name__)


class RAGManagementService:
    """
    Servicio para manejar operaciones de gestión de RAG, incluyendo recarga de documentos.
    """

    async def reload_documents(self) -> Dict[str, Any]:
        """
        Recarga los documentos de playbooks y actualiza el índice FAISS para RAG.

        Returns:
            Dict[str, Any]: Respuesta estructurada con el resultado de la operación.
                - success (bool): Indica si la operación fue exitosa
                - message (str): Mensaje descriptivo del resultado
                - status (str): Estado de la operación
                - details (dict, opcional): Información adicional
        """
        start_time = time.time()

        try:
            # Verificar que el directorio de playbooks existe
            playbooks_dir = "/app/playbooks"
            if not os.path.exists(playbooks_dir):
                return {
                    "success": False,
                    "message": "Directorio de playbooks no encontrado",
                    "status": "Error en la recarga"
                }

            # Contar archivos disponibles antes del procesamiento
            files_count = len([f for f in os.listdir(playbooks_dir) if f.endswith(('.pdf', '.md'))])

            if files_count == 0:
                return {
                    "success": False,
                    "message": "No se encontraron archivos .pdf o .md en el directorio playbooks",
                    "status": "Sin archivos para procesar"
                }

            # Ejecutar la ingesta real de documentos en un thread separado
            logger.info("Iniciando recarga de documentos RAG...")
            rag_processor = RAGProcessor()

            # Usar asyncio para ejecutar el código síncrono en un thread separado
            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor() as executor:
                await loop.run_in_executor(executor, rag_processor.ingest_documents)

            processing_time = time.time() - start_time

            # Verificar que el índice se creó correctamente
            index_path = "/app/faiss_index"
            index_exists = os.path.exists(f"{index_path}/index.faiss")

            if index_exists:
                return {
                    "success": True,
                    "message": f"Recarga de documentos RAG completada exitosamente. {files_count} archivos procesados.",
                    "status": "Recarga completada",
                    "details": {
                        "processed_files": files_count,
                        "index_path": index_path,
                        "processing_time": round(processing_time, 2),
                        "index_created": True
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "La recarga se completó pero no se pudo verificar la creación del índice",
                    "status": "Error en verificación",
                    "details": {
                        "processed_files": files_count,
                        "processing_time": round(processing_time, 2)
                    }
                }

        except ValueError as e:
            # Error específico de configuración de API keys
            logger.error(f"Error de configuración en RAG: {str(e)}")
            processing_time = time.time() - start_time
            return {
                "success": False,
                "message": f"Error de configuración: {str(e)}. Verifique que las claves API estén configuradas correctamente.",
                "status": "Error de configuración",
                "details": {
                    "processing_time": round(processing_time, 2)
                }
            }

        except Exception as e:
            logger.error(f"Error en reload_documents: {str(e)}", exc_info=True)
            processing_time = time.time() - start_time
            return {
                "success": False,
                "message": f"Error interno del servidor al recargar documentos RAG: {str(e)}",
                "status": "Error en la recarga",
                "details": {
                    "processing_time": round(processing_time, 2)
                }
            }


rag_management_service = RAGManagementService()