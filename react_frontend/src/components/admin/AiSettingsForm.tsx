import React from 'react';
import { Card, Button, Select, SelectItem, Textarea, Title } from '@tremor/react';

interface AiSettings {
  model_provider: string;
  model_name: string;
  system_prompt: string;
  isirt_prompt: string;
  parameters: any;
}

interface AvailableModel {
  provider: string;
  model_name: string;
}

interface AiSettingsFormProps {
  aiSettings: AiSettings;
  setAiSettings: React.Dispatch<React.SetStateAction<AiSettings>>;
  providers: string[];
  modelsForProvider: AvailableModel[];
  loading: boolean;
  onSubmit: (e: React.FormEvent) => void;
  onProviderChange: (provider: string) => void;
}

const AiSettingsForm: React.FC<AiSettingsFormProps> = ({
  aiSettings,
  setAiSettings,
  providers,
  modelsForProvider,
  loading,
  onSubmit,
  onProviderChange
}) => {
  return (
    <Card>
      <Title>Configuración del Modelo de IA</Title>
      <form onSubmit={onSubmit} className="mt-6 space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-slate-600">Proveedor del Modelo</label>
            <Select
              value={aiSettings.model_provider}
              onValueChange={onProviderChange}
              className="mt-1"
            >
              <SelectItem value="">Seleccionar proveedor...</SelectItem>
              {providers.map(provider => (
                <SelectItem key={provider} value={provider}>{provider}</SelectItem>
              ))}
            </Select>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-600">Nombre del Modelo</label>
            <Select
              value={aiSettings.model_name}
              onValueChange={(value) => setAiSettings(prev => ({ ...prev, model_name: value }))}
              disabled={!aiSettings.model_provider}
              className="mt-1"
            >
              <SelectItem value="">Seleccionar modelo...</SelectItem>
              {modelsForProvider.map(model => (
                <SelectItem key={model.model_name} value={model.model_name}>
                  {model.model_name}
                </SelectItem>
              ))}
            </Select>
          </div>
        </div>

        <div>
          <label className="text-sm font-medium text-slate-600">User Prompt (SecBot)</label>
          <Textarea
            value={aiSettings.system_prompt}
            onValueChange={(value) => setAiSettings(prev => ({ ...prev, system_prompt: value }))}
            rows={8}
            placeholder="Prompt para el chatbot que interactúa con el usuario final."
            className="mt-1"
          />
        </div>

        <div>
          <label className="text-sm font-medium text-slate-600">ISIRT Prompt (ISIRT-Analyst)</label>
          <Textarea
            value={aiSettings.isirt_prompt}
            onValueChange={(value) => setAiSettings(prev => ({ ...prev, isirt_prompt: value }))}
            rows={8}
            placeholder="Prompt para el chatbot interno del equipo ISIRT, que usa RAG."
            className="mt-1"
          />
        </div>

        <div>
          <label className="text-sm font-medium text-slate-600">Parámetros (JSON)</label>
          <Textarea
            value={typeof aiSettings.parameters === 'object' ? JSON.stringify(aiSettings.parameters, null, 2) : aiSettings.parameters}
            onValueChange={(value) => setAiSettings(prev => ({ ...prev, parameters: value }))}
            rows={5}
            className="mt-1 font-mono text-sm"
          />
        </div>

        <div className="flex justify-end pt-4 border-t border-slate-200">
          <Button
            type="submit"
            loading={loading}
            disabled={loading}
          >
            Guardar Cambios
          </Button>
        </div>
      </form>
    </Card>
  );
};

export default AiSettingsForm;
