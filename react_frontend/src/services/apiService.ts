/**
 * Módulo de Servicio API
 *
 * Este módulo proporciona una interfaz centralizada para todas las comunicaciones API
 * con el sistema backend de gestión de incidentes. Maneja autenticación,
 * formateo de solicitudes, manejo de errores y procesamiento de respuestas.
 */

const API_BASE_URL = '/api/v1';


interface ApiResponse {
  // Definir según sea necesario
}

// Custom error for easier identification
class AuthError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AuthError';
  }
}

export function isAuthError(error: any): error is AuthError {
  return error instanceof AuthError || (error instanceof Error && (error.message.includes('401') || error.message.includes('autorizado')));
}

/**
 * Función de reintento con backoff exponencial
 */
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error: any) {
      if (attempt === maxRetries || !error.shouldRetry) {
        throw error;
      }
      const delay = baseDelay * Math.pow(2, attempt - 1);
      console.log(`Intento ${attempt} falló, reintentando en ${delay}ms...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  throw new Error('Reintentos agotados');
}

/**
 * Función genérica de fetch API que maneja operaciones API comunes.
 * [CON LOGS DE DEPURACIÓN AÑADIDOS Y REINTENTOS]
 */
async function apiFetch(endpoint: string, options: RequestInit = {}, useRetries: boolean = true, allowRedirect: boolean = true, timeoutMs: number = 5000): Promise<any> {
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (options.body && typeof options.body === 'string' && !headers['Content-Type']) {
    try {
      JSON.parse(options.body);
      headers['Content-Type'] = 'application/json';
    } catch (e) {
      // No es JSON
    }
  }

  const fullUrl = `${API_BASE_URL}${endpoint}`;
  console.log(`[DEBUG] API Request: ${options.method || 'GET'} ${fullUrl}`);

  const fetchFn = async () => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs); // Configurable timeout

    try {
      const res = await fetch(fullUrl, {
        ...options,
        headers,
        credentials: 'include', // Ensure cookies are sent with every request
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      console.log(`[DEBUG] API Response: ${res.status} ${res.statusText} for ${fullUrl}`);
      return res;
    } catch (error: any) {
      clearTimeout(timeoutId);

      // Check if this is a timeout abort vs other abort
      if (error.name === 'AbortError') {
        if (controller.signal.aborted && !controller.signal.reason) {
          console.error(`[DEBUG] API Timeout (${timeoutMs}ms) for ${fullUrl}`);
          const timeoutError = new Error(`Request timeout after ${timeoutMs}ms`);
          (timeoutError as any).isTimeout = true;
          throw timeoutError;
        } else {
          console.error(`[DEBUG] API Request aborted for ${fullUrl}:`, controller.signal.reason || 'unknown reason');
          throw error;
        }
      }

      console.error(`[DEBUG] API Fetch Error for ${fullUrl}:`, error);
      throw error;
    }
  };

  const response = useRetries ? await retryWithBackoff(fetchFn) : await fetchFn();

  if (!response.ok) {
    let error;
    const resClone = response.clone(); // Clone the response
    try {
      const errorBody = await response.json();
      const message = (errorBody.detail && typeof errorBody.detail === 'string') ? errorBody.detail : JSON.stringify(errorBody);
      
      if (response.status === 401) {
        error = new AuthError(message);
      } else {
        error = new Error(message);
      }
    } catch (e) {
      // Handle cases where the error response is not valid JSON (e.g., HTML error pages)
      const responseText = await resClone.text(); // Use the clone
      console.error("API response was not valid JSON:", responseText.substring(0, 200)); // Log first 200 chars
      
      if (response.status === 401) {
        error = new AuthError(`Authentication failed. Server returned non-JSON response.`);
      } else {
        error = new Error(`Server error: ${response.status} ${response.statusText}. Response was not valid JSON.`);
      }
    }
    
    // Add retry logic info to the error
    (error as any).shouldRetry = response.status >= 500;
    
    // Conditional redirect for auth errors
    if (isAuthError(error) && allowRedirect && typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
      window.location.href = '/login';
    }

    throw error;
  }

  // Handle successful but empty responses
  if (response.status === 204 || response.headers.get('Content-Length') === '0') {
    return null;
  }

  // Try to parse JSON, with fallback for unexpected non-JSON responses
  const resClone = response.clone();
  try {
    return await response.json();
  } catch (e) {
    console.error("Failed to parse JSON response, although response.ok was true.");
    const responseText = await resClone.text(); // Use the clone
    console.error("Raw response text:", responseText.substring(0, 200));
    // Decide what to return or throw in this unexpected case.
    // Returning null might be safest if the frontend can handle it.
    return null;
  }
}

export const apiService = {
  /**
   * Authenticates a user with email and password.
   */
  login: async (email: string, password: string): Promise<ApiResponse> => {
    const formData = new URLSearchParams({ username: email, password });
    return apiFetch('/login/token', {
        method: 'POST',
        body: formData,
    });
  },

  /**
   * Logs out the current user.
   */
  logout: async (): Promise<ApiResponse> => {
    return apiFetch('/login/logout', { method: 'POST' });
  },

  /**
   * Exchanges a Google authorization code for a session token.
   */
  exchangeGoogleCode: async (code: string, redirect_uri: string): Promise<any> => {
    return apiFetch('/login/google/exchange-code', {
      method: 'POST',
      body: JSON.stringify({ code, redirect_uri }),
    });
  },

  // User endpoints
  getCurrentUser: () => apiFetch('/me/', {}, false, false),
  getUsers: () => apiFetch('/users/'),
  createUser: (userData: any) => apiFetch('/users/', {
    method: 'POST',
    body: JSON.stringify(userData)
  }),
  updateUser: (userId: number, userData: any) => apiFetch(`/users/${userId}`, {
    method: 'PUT',
    body: JSON.stringify(userData)
  }),
  deleteUser: (userId: number) => apiFetch(`/users/${userId}`, { method: 'DELETE' }),
  deactivateUser: (userId: number, reason?: string) => apiFetch(`/users/${userId}/deactivate`, {
    method: 'POST',
    body: reason ? JSON.stringify({ reason }) : undefined
  }),
  activateUser: (userId: number) => apiFetch(`/users/${userId}/activate`, { method: 'POST' }),
  getUserCrossReference: (userId: number) => apiFetch(`/audit/users/${userId}/cross-reference`, {}, false),
  exportUsers: async (filters?: { status?: 'active' | 'inactive', role?: string }) => {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.role) params.append('role', filters.role);
    const query = params.toString();
    const fullUrl = `${API_BASE_URL}/users/export${query ? `?${query}` : ''}`;
    const headers: Record<string, string> = {};
    const res = await fetch(fullUrl, {
      method: 'GET',
      headers,
      credentials: 'include',
    });
    if (!res.ok) {
      throw new Error(`Export failed: ${res.status}`);
    }
    return res.blob();
  },

  // Incident endpoints
  getIncidents: () => apiFetch('/incidents/'),
  getIncidentById: (id: number) => {
    const timestamp = new Date().getTime();
    return apiFetch(`/incidents/${id}?_t=${timestamp}`);
  },
  getIncidentRelatedEntities: (incidentId: number) => apiFetch(`/incidents/${incidentId}/related-entities`),
  createIncident: (payload: any) => {
    const isFormData = payload instanceof FormData;
    return apiFetch('/incidents/', {
      method: 'POST',
      body: isFormData ? payload : JSON.stringify(payload),
      headers: isFormData ? {} : { 'Content-Type': 'application/json' }
    }, true, true, 120000); // 2 minute timeout for incident creation
  },
  updateIncident: (incidentId: number, payload: any) => apiFetch(`/incidents/${incidentId}`, {
    method: 'PUT',
    body: JSON.stringify(payload)
  }),
  addIncidentLog: (incidentId: number, logData: any) => apiFetch(`/incidents/${incidentId}/logs`, {
    method: 'POST',
    body: JSON.stringify(logData)
  }),

  // Chatbot endpoints
  askChatbot: (prompt: string, conversation_id: string) => apiFetch('/reporting/ask', {
    method: 'POST',
    body: JSON.stringify({ prompt: prompt, conversation_id: conversation_id })
  }),

  // AI Settings endpoints
  getAiSettings: () => apiFetch('/ai-settings/'),
  saveAiSettings: (settings: any) => apiFetch('/ai-settings/', {
    method: 'PUT',
    body: JSON.stringify(settings)
  }),
  getAvailableAiModels: (provider?: string) => {
    const query = provider ? `?provider=${provider}` : '';
    return apiFetch(`/ai-settings/available-models${query}`);
  },

  // RAG Settings endpoints
  getRagSettings: () => apiFetch('/rag-settings/'),
  saveRagSettings: (settings: any) => apiFetch('/rag-settings/', {
    method: 'PUT',
    body: JSON.stringify(settings)
  }),
  reloadRag: () => apiFetch('/ai-settings/reload-rag', { method: 'POST' }, true, true, 120000), // 2 minute timeout for RAG reload

  // Classification endpoints
  getAssetTypes: () => apiFetch('/classification/asset-types/'),
  getAssets: (assetTypeId?: number) => {
    const query = assetTypeId ? `?asset_type_id=${assetTypeId}` : '';
    return apiFetch(`/classification/assets/${query}`);
  },
  getIncidentCategories: () => apiFetch('/classification/incident-categories/'),
  getIncidentTypes: (categoryId?: number) => {
    const query = categoryId ? `?incident_category_id=${categoryId}` : '?incident_category_id=1';
    return apiFetch(`/classification/incident-types/${query}`);
  },
  getAttackVectors: () => apiFetch('/classification/attack-vectors/'),

  // Group endpoints
  getGroups: () => apiFetch('/groups/'),
  createGroup: (groupData: any) => apiFetch('/groups/', {
    method: 'POST',
    body: JSON.stringify(groupData)
  }),
  updateGroup: (groupId: number, groupData: any) => apiFetch(`/groups/${groupId}`, {
    method: 'PUT',
    body: JSON.stringify(groupData)
  }),
  deleteGroup: (groupId: number) => apiFetch(`/groups/${groupId}`, { method: 'DELETE' }),

  // Incident suggestions and analysis
  startIncidentSuggestionsTask: (payload: any) => apiFetch('/incident-suggestions/request', {
    method: 'POST',
    body: JSON.stringify(payload)
  }),
  getSuggestionTaskStatus: (taskId: string) => apiFetch(`/incident-suggestions/status/${taskId}`),
  summarizeDialogue: (payload: any) => apiFetch('/incident-reports/summarize', {
    method: 'POST',
    body: JSON.stringify(payload)
  }, true, true, 60000),
  performIncidentTriage: (incidentId: number) => apiFetch(`/incidents/${incidentId}/triage`, {
    method: 'POST'
  }),
  generateISIRTAnalysis: (incidentId: number, analysisRequest: any) => apiFetch(`/incidents/${incidentId}/isirt-analysis`, {
    method: 'POST',
    body: JSON.stringify(analysisRequest)
  }, true, true, 120000),

  // Evidence file endpoints
  getIncidentEvidenceFiles: (incidentId: number) => apiFetch(`/incidents/${incidentId}/evidence`),
  downloadEvidenceFile: async (incidentId: number, evidenceFileId: number) => {
    const fullUrl = `${API_BASE_URL}/incidents/${incidentId}/evidence/${evidenceFileId}/download`;
    const headers: Record<string, string> = {};
    const res = await fetch(fullUrl, {
      method: 'GET',
      headers,
      credentials: 'include',
    });
    if (!res.ok) {
      throw new Error(`Download failed: ${res.status}`);
    }
    return res.blob();
  },

  // RAG Curation
  flagKnowledgeChunk: (payload: { source_name: string, chunk_id: string, notes: string }) => apiFetch('/rag/curate', {
    method: 'POST',
    body: JSON.stringify(payload)
  }),

  // Audit Log endpoints
  getAuditLogs: (filters: any) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, String(value));
      }
    });
    const query = params.toString();
    return apiFetch(`/audit-logs/${query ? `?${query}` : ''}`);
  },
};
