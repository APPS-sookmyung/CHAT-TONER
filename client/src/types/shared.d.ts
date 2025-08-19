// src/types/shared.d.ts
declare module "@shared/schema" {
  // src/shared/schema.ts

  export type UserResponses = {
    formality_level: number;
    friendliness_level: number;
    emotion_level: number;
    directness_level: number;
    uses_abbreviations: boolean;
    uses_emoticons: boolean;
    gratitude_expressions: string[];
    request_expressions: string[];
    situation_responses: Record<string, unknown>;
  };

  export type UserProfile = {
    id: number;
    userId: string;
    baseFormalityLevel: number;
    baseFriendlinessLevel: number;
    baseEmotionLevel: number;
    baseDirectnessLevel: number;
    responses: UserResponses;
    completedAt: Date;
    sessionFormalityLevel?: number;
    sessionFriendlinessLevel?: number;
    sessionEmotionLevel?: number;
    sessionDirectnessLevel?: number;
  };

  export type ConversionRequest = {
    text: string;
    user_profile: UserProfile;
    context?: string;
    negative_preferences?: any;
  };

  export type ConversionResponse = {
    success: boolean;
    original_text?: string;
    converted_texts?: {
      direct: string;
      gentle: string;  
      neutral: string;
    };
    context?: string;
    sentiment_analysis?: any;
    metadata?: any;
    error?: string;
  };
}
