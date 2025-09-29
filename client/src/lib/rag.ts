// client/src/lib/rag.ts
import { RagResponse } from "@/types/rag";

const API = {
  analyzeGrammar: "/api/rag/analyze-grammar",
  suggestExpressions: "/api/rag/suggest-expressions",
} as const;

type CommonBody = {
  query: string;
  context: "general" | "business" | "academic" | "social" | "personal";
  use_styles?: boolean;
  user_profile?: {
    baseFormalityLevel?: number;
    baseFriendlinessLevel?: number;
    baseEmotionLevel?: number;
    baseDirectnessLevel?: number;
    sessionFormalityLevel?: number;
    sessionFriendlinessLevel?: number;
    sessionEmotionLevel?: number;
    sessionDirectnessLevel?: number;
  } | null;
};

async function postJSON<T>(url: string, body: any): Promise<T> {
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) {
    // If backend provides error/detail, expose it directly
    const msg = (data?.error || data?.detail || `HTTP ${r.status}`) as string;
    throw new Error(msg);
  }
  return data as T;
}

export const rag = {
  analyzeGrammar: (body: CommonBody) =>
    postJSON<RagResponse>(API.analyzeGrammar, body),
  suggestExpressions: (body: CommonBody) =>
    postJSON<RagResponse>(API.suggestExpressions, body),
};
