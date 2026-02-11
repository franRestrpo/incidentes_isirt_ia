import React, { useState, useEffect } from 'react';
import { apiService } from '../services/apiService';
import { useNavigate } from 'react-router-dom';
import { Card, Table, TableHead, TableRow, TableHeaderCell, TableBody, TableCell, Badge } from '@tremor/react';
import { capitalizeFirstLetter } from '../utils/textUtils';

interface Incident {
  incident_id: number;
  summary: string;
  status: string;
  severity: string;
  created_at: string;
}

const DashboardPage: React.FC = () => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadIncidents();
  }, []);

  const loadIncidents = async () => {
    try {
      const incidentsData = await apiService.getIncidents();
      setIncidents(incidentsData);
    } catch (error) {
      console.error('Error loading incidents:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const handleViewDetail = (incidentId: number) => {
    navigate(`/incident/${incidentId}`);
  };


  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">Cargando incidentes...</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-slate-900 mb-8">Dashboard de Incidentes</h1>

      <Card>
        <Table>
          <TableHead>
            <TableRow>
              <TableHeaderCell>ID</TableHeaderCell>
              <TableHeaderCell>Título</TableHeaderCell>
              <TableHeaderCell>Estado</TableHeaderCell>
              <TableHeaderCell>Severidad</TableHeaderCell>
              <TableHeaderCell>Fecha</TableHeaderCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {incidents.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8">
                  No hay incidentes para mostrar.
                </TableCell>
              </TableRow>
            ) : (
              incidents.map((incident) => (
                <TableRow 
                  key={incident.incident_id} 
                  className="hover:bg-slate-50 cursor-pointer" 
                  onClick={() => handleViewDetail(incident.incident_id)}
                >
                  <TableCell>INC-{String(incident.incident_id).padStart(3, '0')}</TableCell>
                  <TableCell>{incident.summary}</TableCell>
                  <TableCell>
                    <Badge color={incident.status === 'cerrado' ? 'red' : incident.status === 'resuelto' ? 'gray' : 'blue'}>
                      {capitalizeFirstLetter(incident.status)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge color={incident.severity === 'critico' ? 'red' : incident.severity === 'alto' ? 'orange' : incident.severity === 'medio' ? 'yellow' : 'green'}>
                      {capitalizeFirstLetter(incident.severity || 'N/A')}
                    </Badge>
                  </TableCell>
                  <TableCell>{formatDate(incident.created_at)}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
};

export default DashboardPage;