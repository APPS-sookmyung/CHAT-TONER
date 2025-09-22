export const API = {
  base: '/api',
  conversion: '/api/conversion/convert',
  finetune: {
    convert: '/api/finetune/convert',
  },
  rag: {
    ask: '/api/rag/ask',
    analyzeGrammar: '/api/rag/analyze-grammar',
    suggestExpressions: '/api/rag/suggest-expressions',
  },
  quality: {
    analyze: '/api/quality/analyze',
  },
  profile: (id: string) => `/api/profile/${id}`,
} as const;