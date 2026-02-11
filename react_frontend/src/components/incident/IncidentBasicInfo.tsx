import React from 'react';
import { Metric, Text } from '@tremor/react';

interface Incident {
  ticket_id: string;
  discovery_time: string;
  created_at: string;
  reporter?: { full_name: string };
}

interface IncidentBasicInfoProps {
  incident: Incident;
}

const InfoField: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div>
    <Text>{label}</Text>
    <Metric className="text-lg">{value}</Metric>
  </div>
);

const IncidentBasicInfo: React.FC<IncidentBasicInfoProps> = ({ incident }) => {
  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric', month: 'long', day: 'numeric', 
      hour: '2-digit', minute: '2-digit'
    });
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
      <InfoField label="Código del Incidente" value={incident.ticket_id} />
      <InfoField label="Reportado Por" value={incident.reporter?.full_name || 'N/A'} />
      <InfoField label="Fecha y Hora del Descubrimiento" value={formatDate(incident.discovery_time)} />
      <InfoField label="Fecha y Hora del Reporte" value={formatDate(incident.created_at)} />
    </div>
  );
};

export default IncidentBasicInfo;
