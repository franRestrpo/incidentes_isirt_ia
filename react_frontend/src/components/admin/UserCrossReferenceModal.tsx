/**
 * Modal to display a user's cross-referenced activity.
 */
import React, { useState, useEffect } from 'react';
import { Card, Button, Badge, Table, TableHead, TableRow, TableHeaderCell, TableBody, TableCell, Title, Text } from '@tremor/react';
import { apiService } from '../../services/apiService';
import type { UserCrossReferenceResponse, IncidentRelationship, ActivityLogItem, HistoryLogItem } from '../../types/user_activity';

interface UserCrossReferenceModalProps {
  userId: number;
  onClose: () => void;
}

const UserCrossReferenceModal: React.FC<UserCrossReferenceModalProps> = ({ userId, onClose }) => {
  const [data, setData] = useState<UserCrossReferenceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await apiService.getUserCrossReference(userId);
        setData(result);
      } catch (err) {
        console.error('Error fetching cross-reference:', err);
        setError('Error al cargar las referencias cruzadas. Verifique la consola para más detalles.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [userId]);

  const renderContent = () => {
    if (loading) {
      return <div className="text-center py-8">Cargando...</div>;
    }

    if (error || !data) {
      return (
        <div className="text-center py-8">
          <p className="text-red-600">{error || 'No se encontraron datos.'}</p>
          <Button onClick={onClose} className="mt-4">Cerrar</Button>
        </div>
      );
    }

    const { metrics, incidents, activity_logs, history_logs } = data;

    return (
      <>
        <div className="flex justify-between items-start mb-6">
          <div>
            <Title>Referencias Cruzadas de {metrics.full_name}</Title>
            <Text>{metrics.email}</Text>
          </div>
          <Button onClick={onClose} variant="secondary">Cerrar</Button>
        </div>

        {/* User Info & Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <Card key="info-card">
            <Title>Información</Title>
            <Text><strong>Rol:</strong> <Badge>{metrics.role}</Badge></Text>
            <Text><strong>Estado:</strong> <Badge color={metrics.is_active ? 'green' : 'red'}>{metrics.is_active ? 'Activo' : 'Inactivo'}</Badge></Text>
            <Text><strong>Último Login:</strong> {metrics.last_login ? new Date(metrics.last_login).toLocaleString() : 'N/A'}</Text>
            <Text><strong>Login por Semana:</strong> {metrics.login_frequency_per_week?.toFixed(2) ?? 'N/A'}</Text>
          </Card>
          <Card key="metrics-card">
            <Title>Métricas de Incidentes</Title>
            <Text><strong>Creados:</strong> {metrics.total_incidents_created}</Text>
            <Text><strong>Asignados:</strong> {metrics.total_incidents_assigned}</Text>
            <Text><strong>Resueltos:</strong> {metrics.total_incidents_resolved}</Text>
            <Text><strong>Comentarios:</strong> {metrics.total_comments_made}</Text>
            <Text><strong>Archivos Subidos:</strong> {metrics.total_files_uploaded}</Text>
          </Card>
          <Card key="stats-card">
             <Title>Estadísticas Adicionales</Title>
            <Text><strong>Tipos de Incidentes Comunes:</strong> {metrics.top_incident_types.join(', ') || 'N/A'}</Text>
            <Text><strong>Tiempo Medio de Resolución:</strong> {metrics.average_resolution_time_hours?.toFixed(2) ?? 'N/A'} horas</Text>
            <Title className="mt-2">Incidentes por Estado</Title>
            {Object.entries(metrics.incidents_by_status).map(([status, count], index: number) => (
              <Text key={`${status}-${index}`}><strong>{status}:</strong> {count}</Text>
            ))}
          </Card>
        </div>

        {/* Associated Incidents */}
        <div className="mb-8">
          <Title>Incidentes Asociados ({incidents.length})</Title>
          <Table>
            <TableHead><TableRow><TableHeaderCell>ID</TableHeaderCell><TableHeaderCell>Título</TableHeaderCell><TableHeaderCell>Estado</TableHeaderCell><TableHeaderCell>Relación</TableHeaderCell></TableRow></TableHead>
            <TableBody>
              {incidents.map((inc: IncidentRelationship, index: number) => (
                <TableRow key={`${inc.id}-${index}`}><TableCell>{inc.id}</TableCell><TableCell>{inc.title}</TableCell><TableCell>{inc.status}</TableCell><TableCell><Badge>{inc.relationship_type}</Badge></TableCell></TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Activity Logs */}
        <div className="mb-8">
          <Title>Logs de Actividad Reciente ({activity_logs.length})</Title>
          <Table>
            <TableHead><TableRow><TableHeaderCell>Fecha</TableHeaderCell><TableHeaderCell>Incidente ID</TableHeaderCell><TableHeaderCell>Acción</TableHeaderCell><TableHeaderCell>Comentarios</TableHeaderCell></TableRow></TableHead>
            <TableBody>
              {activity_logs.map((log: ActivityLogItem, index: number) => (
                <TableRow key={`${log.log_id}-${index}`}><TableCell>{new Date(log.timestamp).toLocaleString()}</TableCell><TableCell>{log.incident_id}</TableCell><TableCell>{log.action}</TableCell><TableCell>{log.comments}</TableCell></TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* History Logs */}
        <div>
          <Title>Historial de Cambios Reciente ({history_logs.length})</Title>
          <Table>
            <TableHead><TableRow><TableHeaderCell>Fecha</TableHeaderCell><TableHeaderCell>Incidente ID</TableHeaderCell><TableHeaderCell>Campo Modificado</TableHeaderCell><TableHeaderCell>Valor Anterior</TableHeaderCell><TableHeaderCell>Valor Nuevo</TableHeaderCell></TableRow></TableHead>
            <TableBody>
              {history_logs.map((log: HistoryLogItem, index: number) => (
                <TableRow key={`${log.history_id}-${index}`}><TableCell>{new Date(log.timestamp).toLocaleString()}</TableCell><TableCell>{log.incident_id}</TableCell><TableCell>{log.field_changed}</TableCell><TableCell>{log.old_value}</TableCell><TableCell>{log.new_value}</TableCell></TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </>
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" onClick={onClose}>
      <Card className="max-w-6xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        {renderContent()}
      </Card>
    </div>
  );
};

export default UserCrossReferenceModal;
