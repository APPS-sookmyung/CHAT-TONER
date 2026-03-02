// src/lib/api.ts
import axios, { AxiosInstance, AxiosResponse } from 'axios';

const API_BASE = import.meta.env.PROD
  ? (import.meta.env.VITE_API_URL || '')
  : '';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
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

// ========== v2 Quality Analysis Types ==========
export interface QualityIssue {
  severity: string;
  location: string;
  description: string;
  suggestion: string;
}

export interface QualitySectionResult {
  score: number;
  justification: string;
  issues: QualityIssue[];
  markdown_explanation: string;
}

export interface QualityData {
  grammar: QualitySectionResult;
  formality: QualitySectionResult;
  protocol: QualitySectionResult;
  final_text: string;
  final_text_warning?: string;
  summary: string;
}

export interface QualityAnalysisResponse {
  success: boolean;
  data: QualityData;
  method_used: 'with_rag' | 'without_rag';
  rag_sources_count: number;
  confidence_level: 'high' | 'medium';
  processing_time: number;
  error?: string;
}

export interface RagStatusResponse {
  available: boolean;
  default_index_loaded: boolean;
  default_index_vectors: number;
  company_indexes: string[];
  pdf_dir: string;
  faiss_index_dir: string;
}

// API functions
export const api = {
  // Quality Analysis (v2)
  analyzeQuality: async (data: {
    text: string;
    target: string;
    context: string;
    company_id?: string;
  }): Promise<QualityAnalysisResponse> => {
    const response = await apiClient.post('/api/v1/quality/v2/analyze', data);
    return response.data;
  },

  // RAG Status Check (v2)
  getRagStatus: async (): Promise<RagStatusResponse> => {
    const response = await apiClient.get('/api/v1/quality/v2/rag-status');
    return response.data;
  },

  // Style Conversion
  convertStyle: async (data: {
    text: string;
    user_profile: any;
    context?: string;
    categories?: string[];
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

  // Generate Final Text (v2)
  generateFinalText: async (data: {
    original_text: string;
    target: string;
    context: string;
    grammar_feedback?: string;
    formality_feedback?: string;
    protocol_feedback?: string;
  }): Promise<{ final_text: string; processing_time: number }> => {
    const response = await apiClient.post('/api/v1/quality/v2/generate-final-text', data);
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
