// Backend API base URL for production
const BACKEND_URL = 'https://chattoner-back-184664486594.asia-northeast3.run.app/api/v1';

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
    analyze: `${BACKEND_URL}/quality/analyze`,
  },
  profile: (id: string) => `${BACKEND_URL}/profile/${id}`,
} as const;