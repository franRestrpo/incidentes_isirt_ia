import React from 'react';
import { Card, Title, NumberInput, Button } from '@tremor/react';

interface RagSettings {
  chunk_size: number;
  chunk_overlap: number;
}

interface RagSettingsFormProps {
  ragSettings: RagSettings;
  setRagSettings: React.Dispatch<React.SetStateAction<RagSettings>>;
  ragReloading: boolean;
  onSubmit: (e: React.FormEvent) => void;
  onReload: () => void;
}

const RagSettingsForm: React.FC<RagSettingsFormProps> = ({
  ragSettings,
  setRagSettings,
  ragReloading,
  onSubmit,
  onReload
}) => {
  return (
    <Card>
      <Title>Configuración de RAG</Title>
      <form onSubmit={onSubmit} className="mt-6 space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-slate-600">Tamaño del Chunk (RAG)</label>
            <NumberInput
              value={ragSettings.chunk_size}
              onValueChange={(value) => setRagSettings(prev => ({ ...prev, chunk_size: value }))}
              className="mt-1"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-600">Solapamiento del Chunk (RAG)</label>
            <NumberInput
              value={ragSettings.chunk_overlap}
              onValueChange={(value) => setRagSettings(prev => ({ ...prev, chunk_overlap: value }))}
              className="mt-1"
            />
          </div>
        </div>

        <div className="flex justify-between items-center pt-4 border-t border-slate-200">
          <Button
            type="button"
            onClick={onReload}
            loading={ragReloading}
            disabled={ragReloading}
            variant="secondary"
            icon={() => <i className="fas fa-sync-alt mr-2"></i>}
          >
            Recargar Documentos RAG
          </Button>
          <Button type="submit">
            Guardar Cambios de RAG
          </Button>
        </div>
      </form>
    </Card>
  );
};

export default RagSettingsForm;