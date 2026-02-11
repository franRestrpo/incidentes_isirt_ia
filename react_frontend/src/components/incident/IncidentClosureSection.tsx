import React from 'react';
import { Card, Title, Button, Textarea } from '@tremor/react';
import type { IncidentFormData } from '../../hooks/useIncident';

interface Incident {
  status: string;
}

interface IncidentClosureSectionProps {
  incident: Incident;
  formData: IncidentFormData;
  setFormData: (data: IncidentFormData) => void;
}

const IncidentClosureSection: React.FC<IncidentClosureSectionProps> = ({
  incident,
  formData,
  setFormData
}) => {
  return (
    <Card>
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center">
        <Title>Parte VII: Cierre y Revisión (IRT)</Title>
        {incident.status === 'Cerrado' && (
          <Button 
            onClick={() => alert('Generar reporte final - funcionalidad pendiente')} 
            variant="secondary"
            icon={() => <i className="fas fa-file-alt mr-2"></i>}
            className="mt-4 sm:mt-0"
          >
            Generar Reporte Final para RAG
          </Button>
        )}
      </div>

      <div className="mt-6 space-y-4">
        <div>
          <label className="text-sm font-medium text-slate-600">Acciones Tomadas:</label>
          <Textarea
            value={formData.corrective_actions}
            onValueChange={(value) => setFormData({ ...formData, corrective_actions: value })}
            placeholder="Documente todas las acciones realizadas para contener y resolver el incidente."
            rows={8}
            className="mt-1"
          />
        </div>
        <div>
          <label className="text-sm font-medium text-slate-600">Lecciones Aprendidas:</label>
          <Textarea
            value={formData.lessons_learned}
            onValueChange={(value) => setFormData({ ...formData, lessons_learned: value })}
            placeholder="¿Qué funcionó bien? ¿Qué se puede mejorar en procesos, controles o respuesta?"
            rows={8}
            className="mt-1"
          />
        </div>
        <div>
          <label className="text-sm font-medium text-slate-600">Acciones Correctivas y Preventivas:</label>
          <Textarea
            value={formData.recommendations}
            onValueChange={(value) => setFormData({ ...formData, recommendations: value })}
            placeholder="Liste tareas específicas y asignables para prevenir recurrencia y mejorar la resiliencia."
            rows={8}
            className="mt-1"
          />
        </div>
      </div>
    </Card>
  );
};

export default IncidentClosureSection;
