"""
Esquemas de Pydantic para representar datos en formato de grafo.
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class GraphNode(BaseModel):
    """Representa un nodo en el grafo de ReactFlow."""
    id: str
    type: Optional[str] = None
    data: Dict[str, Any]
    position: Optional[Dict[str, float]] = None
    style: Optional[Dict[str, Any]] = None


class GraphEdge(BaseModel):
    """Representa una arista (conexión) en el grafo de ReactFlow."""
    id: str
    source: str
    target: str
    label: Optional[str] = None
    animated: Optional[bool] = False
    style: Optional[Dict[str, Any]] = None


class RelatedEntitiesResponse(BaseModel):
    """Modelo de respuesta para entidades relacionadas a un nodo del grafo."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
