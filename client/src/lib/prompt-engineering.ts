import type { UserProfile } from "@shared/schema";

export const NEGATIVE_PROMPTS = {
  chatgpt_style: [
    "Of course",
    "I hope this helps",
    "If you have any further questions",
    "I'd be happy to help",
    "Thank you for your understanding",
  ],
  overly_formal: [
    "You (formal)",
    "If I may say so",
    "Taking your precious time",
    "I sincerely thank you",
    "I politely ask",
  ],
  unnecessary_additions: [
    "For your information",
    "In addition",
    "On the other hand",
    "In that respect",
    "To sum up",
    "In conclusion",
  ],
};

export function analyzeUserProfile(userProfile: UserProfile) {
  const responses = (userProfile.responses as any) || {};

  return {
    formalityDescription: getFormalityDescription(
      userProfile.baseFormalityLevel
    ),
    friendlinessDescription: getFriendlinessDescription(
      userProfile.baseFriendlinessLevel
    ),
    emotionDescription: getEmotionDescription(userProfile.baseEmotionLevel),
    usesAbbreviations:
      responses.abbreviation_usage &&
      ["Frequently used", "Very frequently used"].includes(responses.abbreviation_usage[0]),
    usesEmoticons:
      responses.emoticon_usage &&
      ["Frequently used", "Very frequently used", "Used in almost every sentence"].includes(
        responses.emoticon_usage[0]
      ),
    preferredExpressions: {
      gratitude: responses.gratitude_senior || [],
      request: responses.request_colleague || [],
      closing: responses.closing_expressions || [],
      agreement: responses.agreement_expressions || [],
    },
  };
}

function getFormalityDescription(level: number): string {
  if (level >= 8) return "Very polite and formal";
  if (level >= 6) return "Polite";
  if (level >= 4) return "Moderate";
  if (level >= 2) return "Casual";
  return "Very casual";
}

function getFriendlinessDescription(level: number): string {
  if (level >= 8) return "Very friendly and warm";
  if (level >= 6) return "Friendly";
  if (level >= 4) return "Moderate";
  if (level >= 2) return "A bit stiff";
  return "Very formal";
}

function getEmotionDescription(level: number): string {
  if (level >= 8) return "Rich in emotional expression";
  if (level >= 6) return "Appropriate emotional expression";
  if (level >= 4) return "Moderate";
  if (level >= 2) return "Calm";
  return "Very restrained expression";
}

export function validateConversionInput(inputText: string): {
  isValid: boolean;
  error?: string;
} {
  if (!inputText.trim()) {
    return { isValid: false, error: "Please enter text." };
  }

  if (inputText.length < 10) {
    return { isValid: false, error: "Please enter at least 10 characters." };
  }

  if (inputText.length > 2000) {
    return { isValid: false, error: "Please enter 2000 characters or less." };
  }

  return { isValid: true };
}

export function getContextDescription(context: string): string {
  switch (context) {
    case "general":
      return "General conversation or message";
    case "report":
      return "Reports, business documents, official documents";
    case "education":
      return "Educational materials, manuals, guides";
    case "social":
      return "SNS posts, social media";
    default:
      return "General";
  }
}
