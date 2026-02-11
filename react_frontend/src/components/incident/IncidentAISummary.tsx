import React from 'react';
import { TextInput, Textarea } from '@tremor/react';

interface IncidentAISummaryProps {
  summary: string;
  description: string;
  onSummaryChange: (summary: string) => void;
}

const IncidentAISummary: React.FC<IncidentAISummaryProps> = ({
  summary,
  description,
  onSummaryChange
}) => {
  return (
    <div className="space-y-4">
      <div>
        <label className="text-sm font-medium text-slate-700">Título / Resumen Breve:</label>
        <TextInput
          value={summary}
          onValueChange={onSummaryChange}
          className="mt-1"
        />
      </div>
      <div>
        <label className="text-sm font-medium text-slate-700">Descripción Detallada (Generada por IA):</label>
        <Textarea
          value={description || ''}
          rows={15}
          readOnly
          disabled
          className="mt-1 bg-slate-50 text-slate-900 border-slate-300"
        />
      </div>
    </div>
  );
};

export default IncidentAISummary;
