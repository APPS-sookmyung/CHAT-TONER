// client/src/types/rag.ts
export type RagSource = {
  content: string;
  source?: string; // e.g., "business_style.txt"
  metadata?: any;
};

export type RagMetadataBase = {
  query_timestamp: string;
  rag_timestamp: string;
  model_used: string;
  original_text: string;
  context_provided?: boolean;
  query_type?: string;
  query_length?: number;
  context_type?: string;
};

export type RagAnalysisType = "grammar_check" | "expression_improvement";

export type RagResponse = {
  success: boolean;
  answer?: string | null;
  converted_texts?: {
    direct?: string;
    gentle?: string;
    neutral?: string;
  } | null;
  sources?: RagSource[];
  rag_context?: any;
  error?: string | null;
  metadata?: RagMetadataBase & { analysis_type: RagAnalysisType };
};
