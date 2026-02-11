import React from 'react';
import { Button, Select, SelectItem, NumberInput } from '@tremor/react';
import type { IncidentFormData } from '../../hooks/useIncident';

// Interfaces omitidas por brevedad, ya que no cambian

interface IncidentTriageFormProps {
  users: { user_id: number; full_name: string }[];
  groups: { id: number; name: string }[];
  categories: { incident_category_id: number; name: string }[];
  attackVectors: { attack_vector_id: number; name: string }[];
  assetTypes: { asset_type_id: number; name: string }[];
  assets: { asset_id: number; name: string }[];
  incidentTypes: { incident_type_id: number; name: string }[];
  formData: IncidentFormData;
  setFormData: (data: IncidentFormData) => void;
  onAssetTypeChange: (assetTypeId: string) => void;
  onCategoryChange: (categoryId: string) => void;
  onTriage: () => void;
  isUpdating?: boolean;
}

/**
 * Componente de formulario para el triaje y clasificación de un incidente.
 * Permite al analista de seguridad asignar estado, severidad, responsable,
 * y clasificar el incidente según su tipo, activos afectados y vector de ataque.
 * También incluye una funcionalidad para calcular el impacto y ejecutar un triaje con IA.
 *
 * @param {IncidentTriageFormProps} props - Las propiedades del componente.
 * @param {object[]} props.users - Lista de usuarios para asignar como responsables.
 * @param {object[]} props.groups - Lista de grupos para asignar como responsables.
 * @param {object[]} props.categories - Lista de categorías de incidentes.
 * @param {object[]} props.attackVectors - Lista de vectores de ataque.
 * @param {object[]} props.assetTypes - Lista de tipos de activos.
 * @param {object[]} props.assets - Lista de activos específicos (filtrados por tipo).
 * @param {object[]} props.incidentTypes - Lista de tipos de incidentes (filtrados por categoría).
 * @param {IncidentFormData} props.formData - El estado actual del formulario.
 * @param {function} props.setFormData - Función para actualizar el estado del formulario.
 * @param {function} props.onAssetTypeChange - Callback que se ejecuta al cambiar el tipo de activo.
 * @param {function} props.onCategoryChange - Callback que se ejecuta al cambiar la categoría del incidente.
 * @param {function} props.onTriage - Callback para ejecutar el triaje con IA.
 * @param {boolean} [props.isUpdating=false] - Indica si el triaje con IA está en curso.
 * @returns {React.ReactElement} El formulario de triaje de incidentes.
 */
const IncidentTriageForm: React.FC<IncidentTriageFormProps> = ({
  users,
  groups,
  categories,
  attackVectors,
  assetTypes,
  assets,
  incidentTypes,
  formData,
  setFormData,
  onAssetTypeChange,
  onCategoryChange,
  onTriage,
  isUpdating = false
}) => {
  const getTotalImpact = () => {
    return (formData.impact_confidentiality || 0) + (formData.impact_integrity || 0) + (formData.impact_availability || 0);
  };

  return (
    <div className="bg-white rounded-xl shadow-modern-sm border border-slate-200 overflow-hidden">
      <div className="px-6 py-5 border-b border-slate-100">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="bg-teal-100 rounded-lg p-2">
              <i className="fas fa-search text-teal-600 text-sm"></i>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-800">Parte V: Triaje Inteligente</h3>
              <p className="text-sm text-slate-500 mt-1">Análisis automático del incidente</p>
            </div>
          </div>
          <Button
            onClick={onTriage}
            variant="secondary"
            loading={isUpdating}
            disabled={isUpdating}
            icon={() => isUpdating ? <i className="fas fa-cog fa-spin mr-2"></i> : <i className="fas fa-rocket mr-2"></i>}
            className="bg-teal-600 hover:bg-teal-700 text-white px-4 py-2 rounded-lg shadow-modern-sm hover:shadow-modern transition-all duration-200"
          >
            {isUpdating ? 'Ejecutando Triage...' : 'Ejecutar Triage con IA'}
          </Button>
        </div>
      </div>

      <div className="p-6 space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-700">Estado del Incidente</label>
            <Select value={formData.status} onValueChange={(value) => setFormData({ ...formData, status: value })} className="w-full">
              <SelectItem value="Nuevo">Nuevo</SelectItem>
              <SelectItem value="Investigando">Investigando</SelectItem>
              <SelectItem value="Contenido">Contenido</SelectItem>
              <SelectItem value="Erradicado">Erradicado</SelectItem>
              <SelectItem value="Recuperando">Recuperando</SelectItem>
              <SelectItem value="Resuelto">Resuelto</SelectItem>
              <SelectItem value="Cerrado">Cerrado</SelectItem>
            </Select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-700">Severidad</label>
            <Select value={formData.severity} onValueChange={(value) => setFormData({ ...formData, severity: value })} className="w-full">
              <SelectItem value="-- Evaluar según matriz --">-- Evaluar según matriz --</SelectItem>
              <SelectItem value="SEV-1 (Crítico)">SEV-1 (Crítico)</SelectItem>
              <SelectItem value="SEV-2 (Alto)">SEV-2 (Alto)</SelectItem>
              <SelectItem value="SEV-3 (Medio)">SEV-3 (Medio)</SelectItem>
              <SelectItem value="SEV-4 (Bajo)">SEV-4 (Bajo)</SelectItem>
            </Select>
          </div>
          <div className="md:col-span-2 space-y-2">
            <label className="text-sm font-semibold text-slate-700">Responsable Asignado</label>
            <Select value={formData.assigned_to} onValueChange={(value) => setFormData({ ...formData, assigned_to: value })} className="w-full">
              <SelectItem value="">Sin asignar</SelectItem>
              {users.map(user => <SelectItem key={`user-${user.user_id}`} value={`user-${user.user_id}`}>{user.full_name} (Usuario)</SelectItem>)}
              {groups.map(group => <SelectItem key={`group-${group.id}`} value={`group-${group.id}`}>{group.name} (Grupo)</SelectItem>)}
            </Select>
          </div>
        </div>

        <div className="border-t border-slate-100 pt-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-slate-100 rounded-lg p-2">
              <i className="fas fa-tags text-slate-600 text-sm"></i>
            </div>
            <h3 className="text-lg font-semibold text-slate-800">Clasificación del Incidente</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-700">Tipo de Activo Afectado</label>
              <Select value={formData.asset_type_id} onValueChange={(value) => {
                setFormData({ ...formData, asset_type_id: value, asset_id: '' });
                onAssetTypeChange(value);
              }} className="w-full">
                <SelectItem value="">Seleccionar...</SelectItem>
                {assetTypes.map(type => <SelectItem key={type.asset_type_id} value={String(type.asset_type_id)}>{type.name}</SelectItem>)}
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-700">Activo Específico</label>
              <Select value={formData.asset_id} onValueChange={(value) => setFormData({ ...formData, asset_id: value })} className="w-full">
                <SelectItem value="">Seleccionar...</SelectItem>
                {assets.map(asset => <SelectItem key={asset.asset_id} value={String(asset.asset_id)}>{asset.name}</SelectItem>)}
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-700">Categoría del Incidente</label>
              <Select value={formData.incident_category_id} onValueChange={(value) => {
                setFormData({ ...formData, incident_category_id: value, incident_type_id: '' });
                onCategoryChange(value);
              }} className="w-full">
                <SelectItem value="">Seleccionar...</SelectItem>
                {categories.map(cat => <SelectItem key={cat.incident_category_id} value={String(cat.incident_category_id)}>{cat.name}</SelectItem>)}
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-700">Tipo de Incidente</label>
              <Select value={formData.incident_type_id} onValueChange={(value) => setFormData({ ...formData, incident_type_id: value })} className="w-full">
                <SelectItem value="">Seleccionar...</SelectItem>
                {incidentTypes.map(type => <SelectItem key={type.incident_type_id} value={String(type.incident_type_id)}>{type.name}</SelectItem>)}
              </Select>
            </div>
            <div className="md:col-span-2 space-y-2">
              <label className="text-sm font-semibold text-slate-700">Vector de Ataque</label>
              <Select value={formData.attack_vector_id} onValueChange={(value) => setFormData({ ...formData, attack_vector_id: value })} className="w-full">
                <SelectItem value="">Seleccionar...</SelectItem>
                {attackVectors.map(vector => <SelectItem key={vector.attack_vector_id} value={String(vector.attack_vector_id)}>{vector.name}</SelectItem>)}
              </Select>
            </div>
          </div>
        </div>

        <div className="border-t border-slate-100 pt-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-slate-100 rounded-lg p-2">
              <i className="fas fa-chart-bar text-slate-600 text-sm"></i>
            </div>
            <h3 className="text-lg font-semibold text-slate-800">Impacto Organizacional</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-end">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-700">Confidencialidad</label>
              <NumberInput value={formData.impact_confidentiality} onValueChange={(val) => setFormData({ ...formData, impact_confidentiality: val })} min={0} max={10} className="w-full" />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-700">Integridad</label>
              <NumberInput value={formData.impact_integrity} onValueChange={(val) => setFormData({ ...formData, impact_integrity: val })} min={0} max={10} className="w-full" />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-700">Disponibilidad</label>
              <NumberInput value={formData.impact_availability} onValueChange={(val) => setFormData({ ...formData, impact_availability: val })} min={0} max={10} className="w-full" />
            </div>
            <div className="bg-gradient-to-br from-teal-50 to-teal-100 rounded-lg p-4 border border-teal-200">
              <div className="text-xs font-medium text-teal-700 uppercase tracking-wide">Impacto Total</div>
              <div className="text-2xl font-bold text-teal-800 mt-1">{getTotalImpact()}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IncidentTriageForm;
