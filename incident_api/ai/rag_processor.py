"""
Procesador RAG para cargar documentos, extraer metadatos y construir índices vectoriales.
"""

from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    JSONLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
import os
import re
from typing import Any, Dict, List

from incident_api.core.config import settings
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)


def _extract_metadata_from_path(path: str) -> Dict[str, Any]:
    """
    Extrae metadatos estructurados del nombre de archivo.
    """
    filename = os.path.basename(path)
    metadata = {
        "source_name": filename,
        "doc_type": "documentacion", 
        "incident_type": "general", 
        "environment": "general"
    }

    lower_filename = filename.lower()
    if "mitre" in lower_filename or "attack" in lower_filename and lower_filename.endswith(".json"):
        metadata["doc_type"] = "mitre_attack"
        metadata["incident_type"] = "threat_intelligence"
    elif lower_filename.startswith('playbook_'):
        metadata["doc_type"] = "playbook"
        parts = lower_filename.replace('playbook_', '').replace('.md', '').replace('.pdf', '').split('_')
        if len(parts) > 0:
            metadata["incident_type"] = parts[0]
        if len(parts) > 1:
            metadata["environment"] = parts[1]
    
    return metadata

class RAGProcessor:
    """
    Procesador RAG que carga documentos (PDF, Markdown, JSON), extrae metadatos, 
    crea un índice vectorial y construye un retriever auto-consultante.
    """

    def __init__(
        self,
        playbooks_dir: str = "./playbooks",
        faiss_index_path: str = "/app/faiss_index",
    ):
        self.playbooks_dir = playbooks_dir
        self.faiss_index_path = faiss_index_path
        self.embeddings = self._initialize_embeddings()
        self.llm = self._initialize_llm()
        self.metadata_field_info = [
            AttributeInfo(
                name="doc_type",
                description="El tipo de documento. Puede ser 'playbook', 'documentacion', o 'mitre_attack' para la base de datos de MITRE ATT&CK.",
                type="string",
            ),
            AttributeInfo(
                name="incident_type",
                description="La categoría del incidente o tema, como 'phishing', 'ransomware', o 'threat_intelligence' para datos de MITRE.",
                type="string",
            ),
            AttributeInfo(
                name="environment",
                description="El entorno tecnológico, como 'gworkspace', 'windows', 'linux', o 'general'.",
                type="string",
            ),
        ]

    def _initialize_embeddings(self) -> Any:
        """
        Inicializa el modelo de embeddings basado en la configuración disponible (Gemini u OpenAI).
        """
        if settings.GEMINI_API_KEY:
            return GoogleGenerativeAIEmbeddings(
                model="models/embedding-001", google_api_key=settings.GEMINI_API_KEY
            )
        elif settings.OPENAI_API_KEY:
            return OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        else:
            raise ValueError("No se ha configurado ninguna clave API para embeddings (Gemini o OpenAI).")

    def _initialize_llm(self) -> Any:
        """
        Inicializa el modelo de lenguaje basado en la configuración disponible (Gemini u OpenAI).
        """
        if settings.GEMINI_API_KEY:
            return ChatGoogleGenerativeAI(
                model="gemini-pro", google_api_key=settings.GEMINI_API_KEY
            )
        elif settings.OPENAI_API_KEY:
            return ChatOpenAI(model="gpt-4o", openai_api_key=settings.OPENAI_API_KEY)
        else:
            raise ValueError("No se ha configurado ninguna clave API para LLM (Gemini o OpenAI).")

    def ingest_documents(self):
        """
        Ingesta documentos desde el directorio de playbooks, crea chunks y construye el índice FAISS.
        """
        print(f"Cargando documentos desde {self.playbooks_dir}...")

        # Cargador para PDFs
        pdf_loader = DirectoryLoader(self.playbooks_dir, glob="**/*.pdf", loader_cls=PyPDFLoader, show_progress=True)
        # Cargador para Markdown
        md_loader = DirectoryLoader(self.playbooks_dir, glob="**/*.md", loader_cls=UnstructuredMarkdownLoader, show_progress=True)
        # Cargador para JSON (MITRE ATT&CK)
        json_loader = DirectoryLoader(
            self.playbooks_dir, 
            glob="**/*.json", 
            loader_cls=JSONLoader,
            loader_kwargs={'jq_schema': '.objects[].description', 'text_content': False}
        )

        documents = pdf_loader.load() + md_loader.load() + json_loader.load()

        if not documents:
            print(f"Advertencia: No se encontraron documentos (.pdf, .md, .json) en '{self.playbooks_dir}'. El índice RAG no será creado.")
            return

        for doc in documents:
            source_path = doc.metadata.get("source", "")
            if source_path:
                extracted_metadata = _extract_metadata_from_path(source_path)
                doc.metadata.update(extracted_metadata)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)

        print(f"Creando embeddings y construyendo índice FAISS en {self.faiss_index_path}...")
        vector_store = FAISS.from_documents(chunks, self.embeddings)
        vector_store.save_local(self.faiss_index_path)
        print("Ingesta de documentos con metadatos completada.")

    def get_retriever(self, score_threshold: float = 0.7):
        """
        Devuelve un retriever para consultas RAG basado en el índice FAISS.

        Args:
            score_threshold: El umbral de similitud para filtrar documentos.
        """
        if not os.path.exists(self.faiss_index_path):
            raise FileNotFoundError(f"Índice FAISS no encontrado en {self.faiss_index_path}. Por favor, ejecute la ingesta de documentos primero.")

        vector_store = FAISS.load_local(self.faiss_index_path, self.embeddings, allow_dangerous_deserialization=True)
        
        return vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={'score_threshold': score_threshold}
        )