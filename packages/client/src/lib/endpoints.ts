// Unified backend base URL
// - Dev: use Vite proxy (relative '/api')
// - Prod: use VITE_API_URL if provided, else relative
const BASE = (import.meta as any).env?.PROD
  ? ((import.meta as any).env?.VITE_API_URL || '')
  : '';
const BACKEND_URL = `${BASE}/api/v1`;

export const API = {
  base: `${BACKEND_URL}`,
  conversion: `${BACKEND_URL}/conversion/convert`,
  finetune: {
    convert: `${BACKEND_URL}/finetune/convert`,
  },
  rag: {
    ask: `${BACKEND_URL}/rag/ask`,
    analyzeGrammar: `${BACKEND_URL}/rag/analyze-grammar`,
    suggestExpressions: `${BACKEND_URL}/rag/suggest-expressions`,
  },
  quality: {
    analyze: `${BACKEND_URL}/quality/company/analyze`,
  },
  profile: (id: string) => `${BACKEND_URL}/profile/${id}`,
} as const;
