/**
 * Hook personalizado useIncidentReporter
 *
 * Este hook encapsula toda la lógica para gestionar el reporte de incidentes,
 * incluyendo la conversación de chat con IA y el manejo de datos del formulario.
 * Maneja la obtención de datos, gestión de estado, operaciones de chat y envíos de formularios
 * para la página de reporte de incidentes.
 *
 * Responsabilidades:
 * - Gestionar el estado y operaciones de conversación de chat con IA
 * - Gestionar los datos del formulario de reporte de incidentes y validación
 * - Manejar interacciones de API para chat, carga de datos y creación de incidentes
 * - Proporcionar manejadores de eventos para interacciones de UI
 */

import { useState, useEffect, useRef } from 'react';
import { apiService } from '../services/apiService';
import { v4 as uuidv4 } from 'uuid';

interface Message {
  sender: 'user-message' | 'ai-message' | 'ai-status-message';
  text: string;
}

interface ConversationHistory {
  sender: string;
  text: string;
}

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

export const useIncidentReporter = () => {
  // Estado del chat
  const [conversationId] = useState(uuidv4());
  const [chatHistory, setChatHistory] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isAiTyping, setIsAiTyping] = useState(false);
  const [conversationHistory, setConversationHistory] = useState<ConversationHistory[]>([]);
  const conversationStartedRef = useRef(false);

  // Estado del formulario
  const [formData, setFormData] = useState<ReportFormData>({
    reportedBy: '',
    discoveryTime: '',
    summary: '',
    description: '',
    incidentCategoryId: '',
    severity: '',
    assetTypeId: '',
    assetId: '',
    otherAssetLocation: '',
    incidentTypeId: '',
    attackVectorId: '',
    evidenceFiles: []
  });

  // Opciones de dropdown
  const [categories, setCategories] = useState<any[]>([]);
  const [severities] = useState([
    { value: "-- Evaluar según matriz --" },
    { value: "SEV-1 (Crítico)" },
    { value: "SEV-2 (Alto)" },
    { value: "SEV-3 (Medio)" },
    { value: "SEV-4 (Bajo)" }
  ]);
  const [assetTypes, setAssetTypes] = useState<any[]>([]);
  const [assets, setAssets] = useState<any[]>([]);
  const [incidentTypes, setIncidentTypes] = useState<any[]>([]);
  const [attackVectors, setAttackVectors] = useState<any[]>([]);

  // Usuario actual
  const [, setCurrentUser] = useState<any>(null);

  useEffect(() => {
    loadCurrentUser();
    loadInitialData();
    startConversation();
  }, []);

  const loadCurrentUser = async () => {
    try {
      const user = await apiService.getCurrentUser();
      setCurrentUser(user);
      setFormData(prev => ({ ...prev, reportedBy: user.email }));
    } catch (error) {
      console.error('Error loading current user:', error);
    }
  };

  const loadInitialData = async () => {
    try {
      const [cats, ats, avs] = await Promise.all([
        apiService.getIncidentCategories(),
        apiService.getAssetTypes(),
        apiService.getAttackVectors()
      ]);
      setCategories(cats);
      setAssetTypes(ats);
      setAttackVectors(avs);
    } catch (error) {
      console.error('Error loading initial data:', error);
    }
  };

  const startConversation = async () => {
    if (conversationStartedRef.current) return;

    conversationStartedRef.current = true;
    setIsAiTyping(true);
    try {
      const response = await apiService.askChatbot("START_CONVERSATION", conversationId);
      if (response) {
        addMessage(response.response, 'ai-message');
      }
    } catch (error) {
      console.error('Error starting conversation:', error);
      addMessage('Hubo un error al iniciar la conversación. Por favor, recarga la página.', 'ai-message');
    } finally {
      setIsAiTyping(false);
    }
  };

  const addMessage = (text: string, sender: Message['sender']) => {
    const message: Message = { sender, text };
    setChatHistory(prev => [...prev, message]);
    if (sender !== 'ai-status-message') {
      setConversationHistory(prev => [...prev, { sender, text }]);
    }
  };

  const handleUserMessageSubmit = async () => {
    if (!userInput.trim()) return;

    const userText = userInput.trim();
    addMessage(userText, 'user-message');
    setUserInput('');
    setIsAiTyping(true);

    try {
      const response = await apiService.askChatbot(userText, conversationId);
      if (response) {
        let aiText = response.response;
        if (aiText.includes('[CONVERSATION_COMPLETE]')) {
          aiText = aiText.replace('[CONVERSATION_COMPLETE]', '').trim();
          addMessage(aiText, 'ai-message');
          await handleConversationEnd();
        } else {
          addMessage(aiText, 'ai-message');
        }
      }
    } catch (error) {
      console.error('Error getting AI response:', error);
      addMessage('Hubo un error de conexión con el asistente. Por favor, intenta de nuevo.', 'ai-message');
    } finally {
      setIsAiTyping(false);
    }
  };

  const handleConversationEnd = async () => {
    addMessage('Gracias. Analizando la conversación para generar el reporte...', 'ai-status-message');

    try {
      const summaryResponse = await apiService.summarizeDialogue({
        conversation_history: conversationHistory
      });

      if (summaryResponse) {
        setFormData(prev => ({
          ...prev,
          summary: summaryResponse.summary,
          description: summaryResponse.detailed_description
        }));
      } else {
        addMessage('Error al generar resumen. Por favor, completa manualmente.', 'ai-message');
        setFormData(prev => ({
          ...prev,
          summary: '',
          description: ''
        }));
        return;
      }

      const suggestions = await apiService.startIncidentSuggestionsTask({
        description: summaryResponse.detailed_description
      });

      if (suggestions) {
        const taskId = suggestions.task_id;
        let attempts = 0;
        const maxAttempts = 30;

        const checkStatus = async () => {
          try {
            const status = await apiService.getSuggestionTaskStatus(taskId);
            if (status.status === 'completed' && status.result) {
              setFormData(prev => ({
                ...prev,
                incidentCategoryId: status.result.suggested_category_id?.toString() || '',
                severity: status.result.suggested_severity || ''
              }));
              addMessage('Análisis completado. Revisa el reporte y completa los campos restantes.', 'ai-status-message');
            } else if (status.status === 'failed') {
              addMessage('Error al obtener sugerencias. Por favor, completa manualmente.', 'ai-message');
            } else if (attempts < maxAttempts) {
              attempts++;
              setTimeout(checkStatus, 1000);
            } else {
              addMessage('Tiempo de espera agotado. Por favor, completa manualmente.', 'ai-message');
            }
          } catch (error) {
            console.error('Error checking task status:', error);
            addMessage('Error al verificar el estado del análisis.', 'ai-message');
          }
        };

        checkStatus();
      } else {
        addMessage('Error al obtener sugerencias. Por favor, completa manualmente.', 'ai-message');
      }
    } catch (error) {
      console.error('Error in conversation end:', error);
      addMessage('Error al procesar la conversación.', 'ai-message');
    }
  };

  const handleAssetTypeChange = async (assetTypeId: string) => {
    setFormData(prev => ({ ...prev, assetTypeId, assetId: '', otherAssetLocation: '' }));
    if (assetTypeId) {
      try {
        const assetsList = await apiService.getAssets(parseInt(assetTypeId));
        setAssets(assetsList);
      } catch (error) {
        console.error('Error loading assets:', error);
      }
    } else {
      setAssets([]);
    }
  };

  const handleCategoryChange = async (categoryId: string) => {
    setFormData(prev => ({ ...prev, incidentCategoryId: categoryId, incidentTypeId: '' }));
    if (categoryId) {
      try {
        const types = await apiService.getIncidentTypes(parseInt(categoryId));
        setIncidentTypes(types);
      } catch (error) {
        console.error('Error loading incident types:', error);
      }
    } else {
      setIncidentTypes([]);
    }
  };

  const handleAssetChange = (assetId: string) => {
    const selectedAsset = assets.find(a => a.asset_id.toString() === assetId);
    const isOther = selectedAsset?.name?.toLowerCase() === 'otro';
    setFormData(prev => ({
      ...prev,
      assetId,
      otherAssetLocation: isOther ? prev.otherAssetLocation : ''
    }));
  };

  const handleFileChange = (files: FileList | null) => {
    if (files) {
      setFormData(prev => ({ ...prev, evidenceFiles: Array.from(files) }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const formDataToSend = new FormData();

      // Create incident_data JSON as expected by backend
      const incidentData = {
        summary: formData.summary,
        description: formData.description,
        ai_conversation: JSON.stringify(conversationHistory),
        discovery_time: formData.discoveryTime,
        asset_id: formData.assetId ? parseInt(formData.assetId) : null,
        incident_type_id: formData.incidentTypeId ? parseInt(formData.incidentTypeId) : null,
        attack_vector_id: formData.attackVectorId ? parseInt(formData.attackVectorId) : null,
        other_asset_location: formData.otherAssetLocation || null
      };

      formDataToSend.append('incident_data', JSON.stringify(incidentData));

      // Add evidence files
      formData.evidenceFiles.forEach((file) => {
        formDataToSend.append(`evidence_files`, file);
      });

      await apiService.createIncident(formDataToSend);
      alert('Incidente reportado exitosamente');
      // Reiniciar formulario o redirigir - manejado en componente
    } catch (error) {
      console.error('Error submitting incident:', error);
      alert('Error al reportar el incidente');
    }
  };

  return {
    // Estado del chat
    chatHistory,
    userInput,
    setUserInput,
    isAiTyping,
    onSendMessage: handleUserMessageSubmit,

    // Estado del formulario
    formData,
    setFormData,
    categories,
    severities,
    assetTypes,
    assets,
    incidentTypes,
    attackVectors,

    // Manejadores
    handleAssetTypeChange,
    handleCategoryChange,
    handleAssetChange,
    handleFileChange,
    handleSubmit
  };
};