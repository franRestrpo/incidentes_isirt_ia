import { useMemo, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactFlow, { Controls, Background, MiniMap, useNodesState, useEdgesState, addEdge } from 'reactflow';
import type { Node, Edge, OnConnect } from 'reactflow';
import { Dialog, DialogPanel, Title, Text, Button, Card, Flex } from '@tremor/react';
import 'reactflow/dist/style.css';
import { apiService } from '../../services/apiService';

interface GraphProps {
  data: any;
}

const severityColorMap: { [key: string]: { background: string; color: string, borderColor: string } } = {
  'Bajo': { background: '#22c55e', color: '#ffffff', borderColor: '#16a34a' },
  'Medio': { background: '#f59e0b', color: '#ffffff', borderColor: '#d97706' },
  'Alto': { background: '#ef4444', color: '#ffffff', borderColor: '#dc2626' },
  'Crítico': { background: '#8b0000', color: '#ffffff', borderColor: '#000000' },
  'Informativo': { background: '#3b82f6', color: '#ffffff', borderColor: '#2563eb' },
};

const transformDataToGraph = (data: any) => {
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  const incidentNodes = new Set<number>();

  if (!data || !data.metrics) {
    return { initialNodes: [], initialEdges: [] };
  }

  nodes.push({
    id: `user-${data.metrics.user_id}`,
    type: 'input',
    data: { 
      label: `Usuario: ${data.metrics.full_name}`,
      ...data.metrics
    },
    position: { x: 400, y: 50 },
    style: { background: '#facc15', color: '#000', border: '2px solid #eab308', padding: 10, borderRadius: 5 },
  });

  if (data.incidents && data.incidents.length > 0) {
    data.incidents.forEach((incident: any, index: number) => {
      if (!incidentNodes.has(incident.incident_id)) {
        const colors = severityColorMap[incident.severity] || { background: '#9ca3af', color: '#ffffff', borderColor: '#6b7280' };
        nodes.push({
          id: `incident-${incident.incident_id}`,
          data: { 
            label: `Incidente #${incident.ticket_id}`,
            ...incident
          },
          position: { x: 50 + (index * 200), y: 250 },
          style: { 
            background: colors.background,
            color: colors.color,
            border: `2px solid ${colors.borderColor}`,
            padding: 10,
            borderRadius: 5,
            width: 150
          },
        });
        incidentNodes.add(incident.incident_id);
      }

      const isAssigned = incident.relationship_type.toLowerCase().includes('asignado');
      edges.push({
        id: `e-user-incident-${incident.incident_id}`,
        source: `user-${data.metrics.user_id}`,
        target: `incident-${incident.incident_id}`,
        label: incident.relationship_type,
        animated: !isAssigned,
        style: {
          strokeDasharray: isAssigned ? '5 5' : undefined,
          stroke: isAssigned ? '#f59e0b' : '#3b82f6',
        },
      });
    });
  }

  return { initialNodes: nodes, initialEdges: edges };
};

export default function UserActivityGraph({ data }: GraphProps) {
  const { initialNodes, initialEdges } = useMemo(() => transformDataToGraph(data), [data]);
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const navigate = useNavigate();
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [newEdges, setNewEdges] = useState<Edge[]>([]);

  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  useEffect(() => {
    if (newEdges.length > 0) {
      const edgesToAdd = newEdges.filter(newEdge => !edges.find(prevEdge => prevEdge.id === newEdge.id));
      if (edgesToAdd.length > 0) {
        setEdges((prevEdges) => prevEdges.concat(edgesToAdd));
      }
      setNewEdges([]);
    }
  }, [nodes, newEdges, setEdges, edges]);

  const onConnect: OnConnect = (params) => setEdges((eds) => addEdge(params, eds));

  const onNodeClick = (_: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  };

  const handleCloseDialog = () => {
    setSelectedNode(null);
  };

  const handleNavigate = () => {
    if (selectedNode && selectedNode.id.startsWith('incident-')) {
      navigate(`/incident/${selectedNode.data.incident_id}`);
    }
  };

  const handleExpandNode = async () => {
    if (!selectedNode || !selectedNode.id.startsWith('incident-')) return;

    const parentNode = selectedNode;
    handleCloseDialog();

    try {
      const relatedData = await apiService.getIncidentRelatedEntities(parentNode.data.incident_id);
      
      // --- INICIO: Lógica de Layout Circular ---
      const layoutedNodes = relatedData.nodes.map((node: Node, index: number) => {
        const angle = (index / relatedData.nodes.length) * 2 * Math.PI;
        const radius = 150;
        return {
          ...node,
          position: {
            x: parentNode.position.x + radius * Math.cos(angle),
            y: parentNode.position.y + radius * Math.sin(angle),
          },
        };
      });
      // --- FIN: Lógica de Layout Circular ---

      const nodesToAdd = layoutedNodes.filter((newNode: Node) => !nodes.find(prevNode => prevNode.id === newNode.id));
      if (nodesToAdd.length > 0) {
        setNodes((prevNodes) => prevNodes.concat(nodesToAdd));
      }
      setNewEdges(relatedData.edges.filter((newEdge: Edge) => !edges.find(prevEdge => prevEdge.id === newEdge.id)));

    } catch (error) {
      console.error("Failed to expand node:", error);
    }
  };

  const isIncidentNode = selectedNode?.id.startsWith('incident-');

  return (
    <>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>

      <Dialog open={selectedNode !== null} onClose={handleCloseDialog} static={true}>
        <DialogPanel>
          {selectedNode && (
            <Card>
              <Title>{selectedNode.data.label}</Title>
              <div className="mt-4">
                {isIncidentNode ? (
                  <>
                    <Text>Estado: {selectedNode.data.status}</Text>
                    <Text>Severidad: {selectedNode.data.severity}</Text>
                    <Text>Creado: {new Date(selectedNode.data.created_at).toLocaleString()}</Text>
                    <Text>Resumen: {selectedNode.data.summary}</Text>
                  </>
                ) : (
                  <>
                    <Text>Email: {selectedNode.data.email}</Text>
                    <Text>Rol: {selectedNode.data.role}</Text>
                    <Text>Activo: {selectedNode.data.is_active ? 'Sí' : 'No'}</Text>
                  </>
                )}
              </div>
              <Flex justifyContent="end" className="mt-6 space-x-2">
                <Button variant="secondary" onClick={handleCloseDialog}>Cerrar</Button>
                {isIncidentNode && <Button variant="secondary" onClick={handleExpandNode}>Expandir Relaciones</Button>}
                {isIncidentNode && <Button onClick={handleNavigate}>Ir a Detalles</Button>}
              </Flex>
            </Card>
          )}
        </DialogPanel>
      </Dialog>
    </>
  );
}
