import React from 'react';
import { TextInput, Textarea, Select, SelectItem, Button } from '@tremor/react';

interface ReportFormData {
  reportedBy: string;
  discoveryTime: string;
  summary: string;
  description: string;
  incidentCategoryId: string;
  severity: string;
  assetTypeId: string;
  assetId: string;
  otherAssetLocation: string;
  incidentTypeId: string;
  attackVectorId: string;
  evidenceFiles: File[];
}

interface ReportFormProps {
  formData: ReportFormData;
  setFormData: React.Dispatch<React.SetStateAction<ReportFormData>>;
  categories: any[];
  severities: any[];
  assetTypes: any[];
  assets: any[];
  incidentTypes: any[];
  attackVectors: any[];
  handleAssetTypeChange: (assetTypeId: string) => void;
  handleCategoryChange: (categoryId: string) => void;
  handleAssetChange: (assetId: string) => void;
  handleFileChange: (files: FileList | null) => void;
  handleSubmit: (e: React.FormEvent) => void;
}

const ReportForm: React.FC<ReportFormProps> = ({
  formData,
  setFormData,
  categories,
  severities,
  assetTypes,
  assets,
  incidentTypes,
  attackVectors,
  handleAssetTypeChange,
  handleCategoryChange,
  handleAssetChange,
  handleFileChange,
  handleSubmit
}) => {
  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      <fieldset className="rounded-lg border p-4">
        <legend className="text-lg font-semibold text-slate-800 px-2">Datos Iniciales</legend>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div>
            <label className="text-sm font-medium text-slate-600">Reportado Por:</label>
            <TextInput value={formData.reportedBy} readOnly disabled className="mt-1" />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-600">Fecha y Hora del Descubrimiento:</label>
            <input 
              type="datetime-local" 
              value={formData.discoveryTime} 
              onChange={(e) => setFormData(prev => ({ ...prev, discoveryTime: e.target.value }))} 
              required 
              className="w-full mt-1 rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" 
            />
          </div>
        </div>
      </fieldset>

      <fieldset className="rounded-lg border p-4">
        <legend className="text-lg font-semibold text-slate-800 px-2">Parte II: Clasificación (Generada por IA)</legend>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div className="md:col-span-2">
            <label className="text-sm font-medium text-slate-700">Título del Incidente:</label>
            <TextInput value={formData.summary} onValueChange={(value) => setFormData(prev => ({ ...prev, summary: value }))} readOnly disabled placeholder="Será generado por la IA..." className="mt-1 bg-slate-50 text-slate-900 border-slate-300" />
          </div>
          <div className="md:col-span-2">
            <label className="text-sm font-medium text-slate-700">Descripción Detallada:</label>
            <Textarea value={formData.description} onValueChange={(value) => setFormData(prev => ({ ...prev, description: value }))} readOnly disabled rows={10} placeholder="La descripción completa aparecerá aquí." className="mt-1 bg-slate-50 text-slate-900 border-slate-300" />
          </div>
        </div>
      </fieldset>

      <fieldset className="rounded-lg border p-4">
        <legend className="text-lg font-semibold text-slate-800 px-2">Parte III: Activos y Vector de Ataque</legend>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div>
            <label className="text-sm font-medium text-slate-600">Categoría del Incidente:</label>
            <Select value={formData.incidentCategoryId} onValueChange={handleCategoryChange} className="mt-1">
              <SelectItem value="">Seleccione una categoría</SelectItem>
              {categories.map(cat => (
                <SelectItem key={cat.incident_category_id} value={String(cat.incident_category_id)}>{cat.name}</SelectItem>
              ))}
            </Select>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-600">Tipo de Incidente:</label>
            <Select value={formData.incidentTypeId} onValueChange={(value) => setFormData(prev => ({ ...prev, incidentTypeId: value }))} disabled={!formData.incidentCategoryId} className="mt-1">
              <SelectItem value="">Seleccione un tipo</SelectItem>
              {incidentTypes.map(type => (
                <SelectItem key={type.incident_type_id} value={String(type.incident_type_id)}>{type.name}</SelectItem>
              ))}
            </Select>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-600">Tipo de Activo Afectado:</label>
            <Select value={formData.assetTypeId} onValueChange={handleAssetTypeChange} className="mt-1">
              <SelectItem value="">Seleccione un tipo</SelectItem>
              {assetTypes.map(type => (
                <SelectItem key={type.asset_type_id} value={String(type.asset_type_id)}>{type.name}</SelectItem>
              ))}
            </Select>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-600">Activo Específico:</label>
            <Select value={formData.assetId} onValueChange={handleAssetChange} disabled={!formData.assetTypeId} className="mt-1">
              <SelectItem value="">Seleccione un activo</SelectItem>
              {assets.map(asset => (
                <SelectItem key={asset.asset_id} value={String(asset.asset_id)}>{asset.name}</SelectItem>
              ))}
            </Select>
          </div>
          {assets.find(a => a.asset_id.toString() === formData.assetId)?.name?.toLowerCase() === 'otro' && (
            <div className="md:col-span-2">
              <label className="text-sm font-medium text-slate-600">Especifique el Activo:</label>
              <TextInput value={formData.otherAssetLocation} onValueChange={(value) => setFormData(prev => ({ ...prev, otherAssetLocation: value }))} placeholder="Especifique la ubicación o sistema afectado" className="mt-1" />
            </div>
          )}
          <div>
            <label className="text-sm font-medium text-slate-600">Vector de Ataque:</label>
            <Select value={formData.attackVectorId} onValueChange={(value) => setFormData(prev => ({ ...prev, attackVectorId: value }))} className="mt-1">
              <SelectItem value="">Seleccione un vector</SelectItem>
              {attackVectors.map(vector => (
                <SelectItem key={vector.attack_vector_id} value={String(vector.attack_vector_id)}>{vector.name}</SelectItem>
              ))}
            </Select>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-600">Severidad Sugerida:</label>
            <Select value={formData.severity} onValueChange={(value) => setFormData(prev => ({ ...prev, severity: value }))} className="mt-1">
              <SelectItem value="">Seleccione una severidad</SelectItem>
              {severities.map(sev => (
                <SelectItem key={sev.value} value={sev.value}>{sev.value}</SelectItem>
              ))}
            </Select>
          </div>
        </div>
      </fieldset>

      <fieldset className="rounded-lg border p-4">
        <legend className="text-lg font-semibold text-slate-800 px-2">Parte IV: Cargar Evidencia</legend>
        <div className="mt-4">
          <label className="text-sm font-medium text-slate-600">Archivos de Evidencia:</label>
          <input
            type="file"
            id="evidence-files"
            onChange={(e) => handleFileChange(e.target.files)}
            multiple
            className="mt-1 block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          <p className="text-xs text-slate-500 mt-1">Puede seleccionar múltiples archivos.</p>
        </div>
      </fieldset>

      <div className="flex justify-end mt-8">
        <Button type="submit" icon={() => <i className="fas fa-paper-plane mr-2"></i>}>Enviar Reporte Completo</Button>
      </div>
    </form>
  );
};

export default ReportForm;
