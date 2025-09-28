declare module "@shared/schema" {
  // =======================================
  // 기존 타입들
  // =======================================
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

  // =======================================
  // 기업용 분석 추가 타입들
  // =======================================

  // Enums
  export type TargetAudience = "직속상사" | "팀동료" | "타부서담당자" | "클라이언트" | "외부협력업체" | "후배신입";
  export type ContextType = "보고서" | "회의록" | "이메일" | "공지사항" | "메시지";
  export type FeedbackType = "grammar" | "protocol";
  export type FeedbackValue = "good" | "bad";
  export type SeverityLevel = "high" | "medium" | "low";

  // Interfaces
  export interface CompanySuggestionItem {
    id: string;
    category: string;
    original: string;
    suggestion: string;
    reason: string;
    severity: SeverityLevel;
  }

  export interface GrammarSection {
    score: number;
    suggestions: CompanySuggestionItem[];
  }

  export interface ProtocolSection {
    score: number;
    suggestions: CompanySuggestionItem[];
  }

  export interface CompanyAnalysis {
    companyId: string;
    communicationStyle: string;
    complianceLevel: number;
    methodUsed: string;
    processingTime: number;
    ragSourcesCount: number;
  }

  // Request Payloads
  export interface CompanyQualityAnalysisRequest {
    text: string;
    target_audience: TargetAudience;
    context: ContextType;
    company_id: string;
    user_id: string;
    detailed?: boolean;
  }

  export interface UserFeedbackRequest {
    user_id: string;
    company_id: string;
    session_id: string;
    original_text: string;
    suggested_text: string;
    feedback_type: FeedbackType;
    feedback_value: FeedbackValue;
    target_audience: TargetAudience;
    context: ContextType;
    suggestion_category: string;
    scores?: Record<string, number>;
  }

  export interface FinalTextGenerationRequest {
    original_text: string;
    grammar_suggestions: CompanySuggestionItem[];
    protocol_suggestions: CompanySuggestionItem[];
    selected_grammar_ids: string[];
    selected_protocol_ids: string[];
    user_id: string;
    company_id: string;
  }

  // Response Payloads
  export interface CompanyQualityAnalysisResponse {
    grammarScore: number;
    formalityScore: number;
    readabilityScore: number;
    protocolScore: number;
    complianceScore: number;
    grammarSection: GrammarSection;
    protocolSection: ProtocolSection;
    companyAnalysis: CompanyAnalysis;
  }

  export interface DropdownOptions {
    target_audiences: { value: string; label: string; }[];
    contexts: { value: string; label: string; }[];
  }
}