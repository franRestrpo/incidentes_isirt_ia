/**
 * Hook personalizado useAdminSettings
 *
 * Este hook encapsula toda la lógica para gestionar configuraciones de administrador,
 * incluyendo configuración de modelos de IA, configuraciones de RAG y recarga de documentos RAG.
 * Maneja obtención de datos, gestión de estado, operaciones de formulario e interacciones de API
 * para la página de administrador.
 *
 * Responsabilidades:
 * - Obtener configuraciones de IA, configuraciones de RAG y modelos disponibles
 * - Gestionar estado del formulario para configuraciones de IA y RAG
 * - Manejar operaciones de API para guardar configuraciones y recargar RAG
 * - Proporcionar manejadores de eventos para interacciones de UI
 */

import { useState, useEffect } from 'react';
import { apiService } from '../services/apiService';

interface AiSettings {
  model_provider: string;
  model_name: string;
  system_prompt: string;
  isirt_prompt: string;
  parameters: any;
}

interface RagSettings {
  chunk_size: number;
  chunk_overlap: number;
}

interface AvailableModel {
  provider: string;
  model_name: string;
}

export const useAdminSettings = () => {
  const [aiSettings, setAiSettings] = useState<AiSettings>({
    model_provider: '',
    model_name: '',
    system_prompt: '',
    isirt_prompt: '',
    parameters: {}
  });
  const [ragSettings, setRagSettings] = useState<RagSettings>({
    chunk_size: 1000,
    chunk_overlap: 150
  });
  const [availableModels, setAvailableModels] = useState<AvailableModel[]>([]);
  const [loading, setLoading] = useState(false);
  const [ragReloading, setRagReloading] = useState(false);
  const [showRagModal, setShowRagModal] = useState(false);
  const [ragProgress, setRagProgress] = useState(0);
  const [ragStatus, setRagStatus] = useState('');

  useEffect(() => {
    loadAiSettings();
    loadRagSettings();
    loadAvailableModels();
  }, []);

  const loadAiSettings = async () => {
    try {
      const settings = await apiService.getAiSettings();
      setAiSettings(settings);
    } catch (error) {
      console.error('Error loading AI settings:', error);
    }
  };

  const loadRagSettings = async () => {
    try {
      const settings = await apiService.getRagSettings();
      setRagSettings(settings);
    } catch (error) {
      console.error('Error loading RAG settings:', error);
    }
  };

  const loadAvailableModels = async () => {
    try {
      const models = await apiService.getAvailableAiModels();
      setAvailableModels(models);
    } catch (error) {
      console.error('Error loading available models:', error);
    }
  };

  const handleAiSettingsSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      let parameters;
      if (aiSettings.parameters && typeof aiSettings.parameters === 'string') {
        try {
          parameters = JSON.parse(aiSettings.parameters);
        } catch (error) {
          alert('El formato de los parámetros JSON no es válido');
          return;
        }
      } else {
        parameters = aiSettings.parameters;
      }

      const settingsData = {
        ...aiSettings,
        parameters
      };

      await apiService.saveAiSettings(settingsData);
      alert('Configuración de IA guardada exitosamente');
    } catch (error) {
      console.error('Error saving AI settings:', error);
      alert('Error al guardar configuración de IA');
    } finally {
      setLoading(false);
    }
  };

  const handleRagSettingsSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await apiService.saveRagSettings(ragSettings);
      alert('Configuración de RAG guardada exitosamente');
    } catch (error) {
      console.error('Error saving RAG settings:', error);
      alert('Error al guardar configuración de RAG');
    }
  };

  const handleRagReload = async () => {
    setShowRagModal(true);
    setRagProgress(0);
    setRagStatus('Iniciando proceso de recarga...');
    setRagReloading(true);

    try {
      setRagProgress(5);
      setRagStatus('Iniciando recarga de documentos RAG...');

      const response = await apiService.reloadRag();

      if (response.success) {
        setRagProgress(50);
        setRagStatus('Procesando documentos y generando embeddings...');

        await new Promise(resolve => setTimeout(resolve, 1000));

        setRagProgress(80);
        setRagStatus('Construyendo índice FAISS...');

        await new Promise(resolve => setTimeout(resolve, 1000));

        setRagProgress(95);
        setRagStatus('Finalizando y verificando...');

        await new Promise(resolve => setTimeout(resolve, 500));

        setRagProgress(100);
        setRagStatus(`✅ Recarga RAG completada exitosamente\n\n📄 Archivos procesados: ${response.details?.processed_files || 'N/A'}\n📊 Índice creado: ${response.details?.index_created ? 'Sí' : 'No'}`);
        alert('Recarga RAG completada exitosamente');
      } else {
        setRagProgress(100);
        setRagStatus(`❌ ${response.message}`);
        alert('Error en la recarga RAG');
      }
    } catch (error) {
      console.error('RAG reload failed:', error);
      setRagProgress(100);
      setRagStatus('❌ Error interno del servidor');
      alert('Error al procesar la solicitud');
    } finally {
      setRagReloading(false);
    }
  };

  const handleProviderChange = (provider: string) => {
    setAiSettings(prev => ({ ...prev, model_provider: provider, model_name: '' }));
  };

  const providers = [...new Set(availableModels.map(m => m.provider))];
  const modelsForProvider = availableModels.filter(m => m.provider === aiSettings.model_provider);

  return {
    // Estado
    aiSettings,
    setAiSettings,
    ragSettings,
    setRagSettings,
    availableModels,
    loading,
    ragReloading,
    showRagModal,
    setShowRagModal,
    ragProgress,
    ragStatus,
    providers,
    modelsForProvider,

    // Manejadores
    handleAiSettingsSubmit,
    handleRagSettingsSubmit,
    handleRagReload,
    handleProviderChange
  };
};