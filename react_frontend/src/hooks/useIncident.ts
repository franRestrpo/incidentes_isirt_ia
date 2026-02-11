import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiService } from '../services/apiService';
import { useAuth } from '../context/AuthContext';

export interface IncidentFormData {
  summary: string;
  status: string;
  severity: string;
  asset_id: string;
  asset_type_id: string;
  incident_type_id: string;
  incident_category_id: string;
  attack_vector_id: string;
  assigned_to: string;
  impact_confidentiality: number;
  impact_integrity: number;
  impact_availability: number;
  root_cause_analysis: string;
  containment_actions: string;
  recovery_actions: string;
  corrective_actions: string;
  lessons_learned: string;
  recommendations: string;
}

export const useIncident = () => {
  const { id } = useParams<{ id: string }>();
  const { currentUser, loading: authLoading } = useAuth();

  const [incident, setIncident] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [groups, setGroups] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [attackVectors, setAttackVectors] = useState<any[]>([]);
  const [assetTypes, setAssetTypes] = useState<any[]>([]);
  const [assets, setAssets] = useState<any[]>([]);
  const [incidentTypes, setIncidentTypes] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [formData, setFormData] = useState<IncidentFormData>({
    summary: '',
    status: '',
    severity: '',
    asset_id: '',
    asset_type_id: '',
    incident_type_id: '',
    incident_category_id: '',
    attack_vector_id: '',
    assigned_to: '',
    impact_confidentiality: 0,
    impact_integrity: 0,
    impact_availability: 0,
    root_cause_analysis: '',
    containment_actions: '',
    recovery_actions: '',
    corrective_actions: '',
    lessons_learned: '',
    recommendations: ''
  });

  const loadIncidentData = async () => {
    if (!id || !currentUser) {
      return;
    }

    setLoading(true);
    try {
      console.log(`[${new Date().toISOString()}] Loading incident data for ID: ${id}`);

      const [incidentData, usersData, groupsData, categoriesData, attackVectorsData, assetTypesData] = await Promise.all([
        apiService.getIncidentById(parseInt(id)),
        apiService.getUsers(),
        apiService.getGroups(),
        apiService.getIncidentCategories(),
        apiService.getAttackVectors(),
        apiService.getAssetTypes(),
      ]);

      setIncident(incidentData);
      setUsers(usersData);
      setGroups(groupsData);
      setCategories(categoriesData);
      setAttackVectors(attackVectorsData);
      setAssetTypes(assetTypesData);
      setLogs(incidentData.logs || []);

      if (incidentData.incident_type?.incident_category_id) {
        const types = await apiService.getIncidentTypes(incidentData.incident_type.incident_category_id);
        setIncidentTypes(types);
      }

      if (incidentData.asset?.asset_type_id) {
        const assetsData = await apiService.getAssets(incidentData.asset.asset_type_id);
        setAssets(assetsData);
      }

      setFormData({
        summary: incidentData.summary || '',
        status: incidentData.status || '',
        severity: incidentData.severity || '',
        asset_id: incidentData.asset_id?.toString() || '',
        asset_type_id: incidentData.asset?.asset_type_id?.toString() || '',
        incident_type_id: incidentData.incident_type_id?.toString() || '',
        incident_category_id: incidentData.incident_type?.incident_category_id?.toString() || '',
        attack_vector_id: incidentData.attack_vector_id?.toString() || '',
        assigned_to: incidentData.assignee ? `user-${incidentData.assignee.user_id}` :
                      incidentData.assignee_group ? `group-${incidentData.assignee_group.id}` : '',
        impact_confidentiality: incidentData.impact_confidentiality || 0,
        impact_integrity: incidentData.impact_integrity || 0,
        impact_availability: incidentData.impact_availability || 0,
        root_cause_analysis: incidentData.root_cause_analysis || '',
        containment_actions: incidentData.containment_actions || '',
        recovery_actions: incidentData.recovery_actions || '',
        corrective_actions: incidentData.corrective_actions || '',
        lessons_learned: incidentData.lessons_learned || '',
        recommendations: incidentData.recommendations || ''
      });

    } catch (error) {
      console.error(`[${new Date().toISOString()}] Error loading incident data:`, error);
      alert('Error al cargar los datos del incidente. Por favor, intente de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  const handleAssetTypeChange = async (assetTypeId: number) => {
    setAssets([]);
    if (assetTypeId) {
      const assetsData = await apiService.getAssets(assetTypeId);
      setAssets(assetsData);
    }
  };

  const handleCategoryChange = async (categoryId: number) => {
    setIncidentTypes([]);
    if (categoryId) {
      const types = await apiService.getIncidentTypes(categoryId);
      setIncidentTypes(types);
    }
  };

  const handleTriage = async () => {
    if (!id || !incident?.description) {
      alert('La descripción del incidente es necesaria para el triaje con IA.');
      return;
    }
    setUpdating(true);

    try {
      const { task_id } = await apiService.startIncidentSuggestionsTask({ description: incident.description });

      const poll = async (taskId: string): Promise<any> => {
        const statusResponse = await apiService.getSuggestionTaskStatus(taskId);
        if (statusResponse.status === 'completed') {
          return statusResponse.result;
        } else if (statusResponse.status === 'failed') {
          throw new Error(statusResponse.result?.error || 'La tarea de análisis de IA falló.');
        } else {
          await new Promise(resolve => setTimeout(resolve, 2000));
          return poll(taskId);
        }
      };

      const suggestions = await poll(task_id);

      if (suggestions) {
        setFormData(prevData => ({
          ...prevData,
          summary: suggestions.suggested_title || prevData.summary,
          severity: suggestions.suggested_severity || prevData.severity,
          incident_category_id: suggestions.suggested_category_id?.toString() || prevData.incident_category_id,
          incident_type_id: suggestions.suggested_incident_type_id?.toString() || prevData.incident_type_id,
          assigned_to: suggestions.suggested_user_id ? `user-${suggestions.suggested_user_id}` : prevData.assigned_to,
        }));

        if (suggestions.suggested_category_id) {
          handleCategoryChange(suggestions.suggested_category_id);
        }
      }

    } catch (error) {
      console.error('Error performing triage:', error);
      alert('Ocurrió un error al ejecutar el triaje con IA.');
    } finally {
      setUpdating(false);
    }
  };

  const handleISIRTAnalysis = async (analysisRequest: any = {}) => {
    if (!id) return;
    setUpdating(true);
    try {
      const actualRequest = analysisRequest && analysisRequest._reactName ? {} : analysisRequest;
      const analysisResult = await apiService.generateISIRTAnalysis(parseInt(id), actualRequest);

      if (analysisResult && analysisResult.enrichment) {
        const enrichment = analysisResult.enrichment;
        // Update the form data with the new analysis
        setFormData(prevData => ({
          ...prevData,
          root_cause_analysis: enrichment.triage_analysis?.potential_attack_vector || prevData.root_cause_analysis,
          containment_actions: enrichment.response_recommendations?.containment_steps?.join('\n') || prevData.containment_actions,
          recovery_actions: enrichment.response_recommendations?.recovery_steps?.join('\n') || prevData.recovery_actions,
          corrective_actions: enrichment.response_recommendations?.eradication_steps?.join('\n') || prevData.corrective_actions, // Note: Mapped from eradication
          lessons_learned: "", // This is not in the enrichment response, so we clear it or handle it differently
          summary: enrichment.executive_summary || prevData.summary,
          severity: enrichment.triage_analysis?.initial_severity_assessment || prevData.severity,
          recommendations: enrichment.communication_guidelines || prevData.recommendations,
        }));

        // Refresh the entire incident data from the backend to get the new ai_recommendations
        await loadIncidentData();
      }

    } catch (error) {
      console.error('Error generating ISIRT analysis:', error);
      alert('Ocurrió un error al generar el análisis ISIRT.');
    } finally {
      setUpdating(false);
    }
  };

  const handleUpdate = async () => {
    if (!id) return;
    setUpdating(true);
    try {
      await apiService.updateIncident(parseInt(id), formData);
      await loadIncidentData();
    } catch (error) {
      console.error('Error updating incident:', error);
    } finally {
      setUpdating(false);
    }
  };

  useEffect(() => {
    if (id && currentUser && !authLoading) {
      loadIncidentData();
    }
  }, [id, currentUser, authLoading]);

  return {
    incident,
    users,
    groups,
    categories,
    attackVectors,
    assetTypes,
    assets,
    incidentTypes,
    logs,
    loading: loading || authLoading,
    updating,
    formData,
    setFormData,
    handleAssetTypeChange,
    handleCategoryChange,
    handleTriage,
    handleISIRTAnalysis,
    handleUpdate,
    loadIncidentData
  };
};
