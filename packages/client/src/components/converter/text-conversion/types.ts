export interface ConversionResponse {
  conversionId: number;
  versions: {
    direct: string;
    gentle: string;
    neutral: string;
  };
  analysis: {
    formalityLevel: number;
    friendlinessLevel: number;
    emotionLevel: number;
  };
}

export type ConversionContext = "general" | "report" | "education" | "social";

export type VersionType = "direct" | "gentle" | "neutral";

export interface NegativePreferences {
  rhetoricLevel: string;
  repetitionTolerance: string;
  punctuationStyle: string;
  contentFocus: string;
  bulletPreference: string;
  emoticonPolicy: string;
}

export const DEFAULT_NEGATIVE_PREFERENCES: NegativePreferences = {
  rhetoricLevel: "moderate",
  repetitionTolerance: "moderate",
  punctuationStyle: "standard",
  contentFocus: "balanced",
  bulletPreference: "minimal",
  emoticonPolicy: "contextual",
};
