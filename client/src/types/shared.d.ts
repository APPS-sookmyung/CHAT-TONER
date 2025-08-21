// src/types/shared.d.ts
declare module "@shared/schema" {
  // src/shared/schema.ts

  export type UserProfile = {
    id?: number;
    baseFormalityLevel: number;
    baseFriendlinessLevel: number;
    baseEmotionLevel: number;
    baseDirectnessLevel: number;
    sessionFormalityLevel?: number;
    sessionFriendlinessLevel?: number;
    sessionEmotionLevel?: number;
    sessionDirectnessLevel?: number;
    completedAt?: Date;
    responses?: UserResponses;
  };

  export type UserResponses = {
    formality_level: number;
    friendliness_level: number;
    emotion_level: number;
    directness_level: number;
    uses_abbreviations?: boolean;
    uses_emoticons?: boolean;
    gratitude_expressions?: string[] | Record<string, any>;
    request_expressions?: string[] | Record<string, any>;
    situation_responses?: string[] | Record<string, any>;
  };

  export type NegativePreferences = {
    rhetoricLevel?: string;
    repetitionTolerance?: string;
    punctuationStyle?: string;
    contentFocus?: string;
    bulletPreference?: string;
    emoticonPolicy?: string;
  };

  export type ConversionRequest = {
    text: string;
    user_profile: UserProfile;
    context?: string;
    negative_preferences?: NegativePreferences;
  };

  export type ConversionResponse = {
    success: boolean;
    original_text?: string;
    converted_texts?: Record<string, string>;
    context?: string;
    sentiment_analysis?: Record<string, any>;
    metadata?: Record<string, any>;
    error?: string;
  };

  export type QualityAnalysisRequest = {
    text: string;
  };

  export type SuggestionItem = {
    original: string;
    suggestion: string;
    reason: string;
  };

  export type QualityAnalysisResponse = {
    grammarScore: number;
    formalityScore: number;
    readabilityScore: number;
    suggestions: SuggestionItem[];
  };

  export type ContextSuggestionsRequest = {
    text: string;
    context: string; // business, casual, report
  };

  export type ContextSuggestionsResponse = {
    suggestions: SuggestionItem[];
    count: number;
  };

  export type FeedbackRequest = {
    original_text: string;
    converted_text: string;
    feedback_score: number; // 1-5
    feedback_comment: string;
  };

  export type FeedbackResponse = {
    success: boolean;
    message: string;
  };

  export type FinetuneRequest = {
    text: string;
    user_profile: Record<string, any>;
    context?: "business" | "report" | "personal";
    force_convert?: boolean;
  };

  export type FinetuneResponse = {
    success: boolean;
    converted_text?: string;
    lora_output?: string;
    method: string;
    reason: string;
    forced?: boolean;
    error?: string;
    metadata?: Record<string, any>;
    timestamp?: string; // datetime in Python is string in TS
  };

  export type FinetuneStatusResponse = {
    lora_status: "ready" | "not_ready";
    lora_model_path: string;
    services_available: boolean;
    base_model_loaded: boolean;
    device: string;
    model_name: string;
  };
}
