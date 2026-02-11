import React, { useState } from 'react';
import { apiService } from '../../services/apiService';
import { Card, Title, Textarea, Button, Text } from '@tremor/react';

interface IncidentLog {
  log_id: number;
  action: string;
  comments?: string;
  field_modified?: string;
  old_value?: string;
  new_value?: string;
  timestamp: string;
  user: {
    full_name: string;
  };
}

interface IncidentLogTimelineProps {
  logs: IncidentLog[];
  incidentId: number;
  onLogAdded: () => void;
}

const IncidentLogTimeline: React.FC<IncidentLogTimelineProps> = ({ logs, incidentId, onLogAdded }) => {
  const [newLogEntry, setNewLogEntry] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('es-ES', { dateStyle: 'medium', timeStyle: 'short' });
  };

  const handleAddLogEntry = async () => {
    if (!newLogEntry.trim()) return;
    setIsSubmitting(true);
    try {
      await apiService.addIncidentLog(incidentId, {
        action: 'Entrada manual',
        comments: newLogEntry.trim()
      });
      setNewLogEntry('');
      onLogAdded();
    } catch (error) {
      console.error('Error adding log entry:', error);
      alert('Error al añadir entrada al registro');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getEventIcon = (action: string, field_modified?: string) => {
    if (action.includes('Estado') || field_modified === 'status') return 'fas fa-check';
    if (action.includes('Asignación') || field_modified === 'assigned_to') return 'fas fa-user';
    if (action.includes('Comentario') || action === 'Entrada manual') return 'fas fa-comment';
    if (field_modified === 'severity') return 'fas fa-shield-alt';
    return 'fas fa-history';
  };

  const formatRelativeTime = (dateString: string) => {
    const now = new Date();
    const date = new Date(dateString);
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'ahora mismo';
    if (diffMins < 60) return `hace ${diffMins} minuto${diffMins > 1 ? 's' : ''}`;
    if (diffHours < 24) return `hace ${diffHours} hora${diffHours > 1 ? 's' : ''}`;
    if (diffDays < 7) return `hace ${diffDays} día${diffDays > 1 ? 's' : ''}`;
    return formatDate(dateString);
  };

  const formatConciseAction = (log: IncidentLog) => {
    if (log.field_modified) {
      const fieldName = log.field_modified === 'status' ? 'Estado' :
                       log.field_modified === 'assigned_to' ? 'Asignación' :
                       log.field_modified === 'severity' ? 'Severidad' :
                       log.field_modified;
      return (
        <div>
          <strong>{log.user.full_name}</strong> cambió el <strong>{fieldName}</strong>
          <br />
          de <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs">{log.old_value}</span> a <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">{log.new_value}</span>
        </div>
      );
    }
    return (
      <div>
        <strong>{log.user.full_name}</strong> {log.action.toLowerCase()}
        {log.comments && `: ${log.comments}`}
      </div>
    );
  };

  return (
    <Card>
      <Title>Bitácora del Incidente</Title>

      {/* Add Entry Form at Top */}
      <div className="mt-4">
        <label htmlFor="log-entry-input" className="text-sm font-medium text-slate-600">
          Añadir Entrada a Bitácora:
        </label>
        <Textarea
          id="log-entry-input"
          placeholder="Describe la acción realizada o el hallazgo..."
          value={newLogEntry}
          onValueChange={setNewLogEntry}
          rows={3}
          className="mt-1"
        />
        <Button
          onClick={handleAddLogEntry}
          disabled={!newLogEntry.trim() || isSubmitting}
          loading={isSubmitting}
          className="w-full mt-2"
        >
          Añadir Entrada
        </Button>
      </div>

      <div className="mt-6 h-[500px] overflow-y-auto pr-2">
        <div className="relative border-l-2 border-slate-200 pl-6 space-y-6">
          {logs.length > 0 ? (
            logs.map((log) => (
              <div key={log.log_id} className="relative">
                <div className="absolute -left-[35px] top-1 flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 ring-8 ring-white">
                  <i className={`${getEventIcon(log.action, log.field_modified)} text-blue-600 text-xs`}></i>
                </div>
                <div>
                  <div className="text-sm text-slate-700">
                    {formatConciseAction(log)}
                  </div>
                  <Text className="text-xs text-slate-500 mt-1" title={formatDate(log.timestamp)}>
                    {formatRelativeTime(log.timestamp)}
                  </Text>
                </div>
              </div>
            ))
          ) : (
            <Text className="italic text-center p-4">No hay entradas en la bitácora.</Text>
          )}
        </div>
      </div>
    </Card>
  );
};

export default IncidentLogTimeline;
