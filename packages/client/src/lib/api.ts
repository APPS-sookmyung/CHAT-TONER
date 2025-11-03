// src/lib/api.ts
import axios, { AxiosInstance, AxiosResponse } from 'axios';

const API_BASE = import.meta.env.PROD 
  ? (import.meta.env.VITE_API_URL || '') 
  : '';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add any auth headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// API functions
export const api = {
  // Quality Analysis
  analyzeQuality: async (data: {
    text: string;
    company_id: string;
    user_id: string;
    target_audience: string;
    context: string;
    detailed?: boolean;
  }) => {
    const response = await apiClient.post('/api/v1/quality/company/analyze', data);
    return response.data;
  },

  // Style Conversion
  convertStyle: async (data: {
    text: string;
    user_profile: any;
    context?: string;
    negative_preferences?: any;
  }) => {
    const response = await apiClient.post('/api/v1/conversion/convert', data);
    return response.data;
  },

  // Document Upload
  uploadDocuments: async (files: File[]) => {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    
    const response = await apiClient.post('/api/v1/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Survey Responses
  submitSurvey: async (data: {
    tenant_id: string;
    user_id: string;
    answers: Record<string, string>;
  }) => {
    const response = await apiClient.post('/api/v1/surveys/onboarding-intake/responses', data);
    return response.data;
  },

  // Health Check
  healthCheck: async () => {
    const response = await apiClient.get('/');
    return response.data;
  },

  // Company Status
  getCompanyStatus: async (companyId: string) => {
    const response = await apiClient.get(`/api/v1/quality/company/${companyId}/status`);
    return response.data;
  },

  // Test Company Setup
  createTestCompany: async (companyId: string) => {
    const response = await apiClient.post('/api/v1/quality/company/test-setup', { company_id: companyId });
    return response.data;
  },

  // Get Dropdown Options
  getDropdownOptions: async () => {
    const response = await apiClient.get('/api/v1/quality/company/options');
    return response.data;
  },

  // Generate Final Text (LLM-based integration)
  generateFinalText: async (data: {
    original_text: string;
    grammar_suggestions: any[];
    protocol_suggestions: any[];
    selected_grammar_ids: string[];
    selected_protocol_ids: string[];
    user_id: string;
    company_id: string;
  }) => {
    const response = await apiClient.post('/api/v1/quality/company/generate-final', data);
    return response.data;
  },

  // Document Management
  getDocuments: async (subdir?: string) => {
    const params = subdir ? { subdir } : {};
    const response = await apiClient.get('/api/v1/documents/', { params });
    return response.data;
  },

  deleteDocument: async (documentName: string) => {
    const response = await apiClient.delete(`/api/v1/documents/${encodeURIComponent(documentName)}`);
    return response.data;
  },

  // PDF Summarization
  summarizePDF: async (data: {
    document_name: string;
    summary_type: 'brief' | 'detailed' | 'bullet_points';
  }) => {
    const response = await apiClient.post('/api/v1/documents/summarize-pdf', data);
    return response.data;
  },

  summarizeText: async (data: {
    text: string;
    summary_type: 'brief' | 'detailed' | 'bullet_points';
  }) => {
    const response = await apiClient.post('/api/v1/documents/summarize-text', data);
    return response.data;
  }
};

// Legacy fetch-based functions for backward compatibility
export async function apiGet<T>(path: string, init: RequestInit = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(init.headers || {}) },
    ...init,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return (await res.json()) as T;
}

export async function apiPost<T>(path: string, data: any, init: RequestInit = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(init.headers || {}) },
    body: JSON.stringify(data),
    ...init,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return (await res.json()) as T;
}
