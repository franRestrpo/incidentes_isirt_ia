import React from 'react';
import { Button, Textarea } from '@tremor/react';
import type { IncidentFormData } from '../../hooks/useIncident';

interface IncidentAnalysisSectionProps {
  formData: IncidentFormData;
  setFormData: (data: IncidentFormData) => void;
  onISIRTAnalysis: () => void;
  isUpdating?: boolean;
}

const IncidentAnalysisSection: React.FC<IncidentAnalysisSectionProps> = ({
  formData,
  setFormData,
  onISIRTAnalysis,
  isUpdating = false
}) => {
  return (
    <div className="bg-white rounded-xl shadow-modern-sm border border-slate-200 overflow-hidden">
      <div className="px-6 py-5 border-b border-slate-100">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="bg-teal-100 rounded-lg p-2">
              <i className="fas fa-brain text-teal-600 text-sm"></i>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-800">Parte VI: Análisis y Respuesta ISIRT</h3>
              <p className="text-sm text-slate-500 mt-1">Análisis inteligente del incidente</p>
            </div>
          </div>
          <Button
            onClick={onISIRTAnalysis}
            variant="secondary"
            loading={isUpdating}
            disabled={isUpdating}
            icon={() => isUpdating ? <i className="fas fa-cog fa-spin mr-2"></i> : <i className="fas fa-robot mr-2"></i>}
            className="bg-teal-600 hover:bg-teal-700 text-white px-4 py-2 rounded-lg shadow-modern-sm hover:shadow-modern transition-all duration-200"
          >
            {isUpdating ? 'Generando Análisis...' : 'Generar Análisis con IA'}
          </Button>
        </div>
      </div>

      <div className="p-6 space-y-6">
        <div className="space-y-3">
          <label className="text-sm font-semibold text-slate-700 flex items-center gap-2">
            <i className="fas fa-search text-slate-500 text-xs"></i>
            Análisis de Causa Raíz
          </label>
          <Textarea
            value={formData.root_cause_analysis}
            onValueChange={(value) => setFormData({ ...formData, root_cause_analysis: value })}
            placeholder="Explique la vulnerabilidad fundamental que permitió el incidente."
            rows={6}
            className="w-full resize-none border-slate-200 focus:border-teal-500 focus:ring-teal-500 rounded-lg"
          />
        </div>
        <div className="space-y-3">
          <label className="text-sm font-semibold text-slate-700 flex items-center gap-2">
            <i className="fas fa-shield-alt text-slate-500 text-xs"></i>
            Acciones de Contención
          </label>
          <Textarea
            value={formData.containment_actions}
            onValueChange={(value) => setFormData({ ...formData, containment_actions: value })}
            placeholder="Liste las acciones inmediatas tomadas para contener el incidente."
            rows={6}
            className="w-full resize-none border-slate-200 focus:border-teal-500 focus:ring-teal-500 rounded-lg"
          />
        </div>
        <div className="space-y-3">
          <label className="text-sm font-semibold text-slate-700 flex items-center gap-2">
            <i className="fas fa-tools text-slate-500 text-xs"></i>
            Acciones de Recuperación
          </label>
          <Textarea
            value={formData.recovery_actions}
            onValueChange={(value) => setFormData({ ...formData, recovery_actions: value })}
            placeholder="Describa los pasos para restaurar sistemas y servicios."
            rows={6}
            className="w-full resize-none border-slate-200 focus:border-teal-500 focus:ring-teal-500 rounded-lg"
          />
        </div>
        <div className="space-y-3">
          <label className="text-sm font-semibold text-slate-700 flex items-center gap-2">
            <i className="fas fa-lightbulb text-slate-500 text-xs"></i>
            Lecciones Aprendidas
          </label>
          <Textarea
            value={formData.lessons_learned}
            onValueChange={(value) => setFormData({ ...formData, lessons_learned: value })}
            placeholder="¿Qué funcionó bien? ¿Qué se puede mejorar?"
            rows={6}
            className="w-full resize-none border-slate-200 focus:border-teal-500 focus:ring-teal-500 rounded-lg"
          />
        </div>
        <div className="space-y-3">
          <label className="text-sm font-semibold text-slate-700 flex items-center gap-2">
            <i className="fas fa-check-circle text-slate-500 text-xs"></i>
            Acciones Correctivas
          </label>
          <Textarea
            value={formData.corrective_actions}
            onValueChange={(value) => setFormData({ ...formData, corrective_actions: value })}
            placeholder="Medidas específicas para prevenir recurrencia."
            rows={6}
            className="w-full resize-none border-slate-200 focus:border-teal-500 focus:ring-teal-500 rounded-lg"
          />
        </div>
      </div>
    </div>
  );
};

export default IncidentAnalysisSection;
