import type { UserProfile } from "@shared/schema";
import type { ConversionResponse, ConversionContext, VersionType } from "./types";

const CONTEXT_ADJUSTMENTS = {
  general: { formality: 0, friendliness: 0, emotion: 0 },
  report: { formality: 2, friendliness: -1, emotion: -1 },
  education: { formality: 1, friendliness: 1, emotion: 0 },
  social: { formality: -2, friendliness: 2, emotion: 1 },
} as const;

const transformText = (
  text: string,
  style: VersionType,
  adjustedFormality: number,
  adjustedFriendliness: number,
  adjustedEmotion: number
): string => {
  let transformed = text;

  // Direct style - brief and clear
  if (style === "direct") {
    transformed = transformed
      .replace(/Could you please\?/g, "Please do.")
      .replace(/I would appreciate it if you could do it/g, "Please do")
      .replace(/I ask of you/g, "Please do")
      .replace(/a little/g, "")
      .replace(/Can you do it for me/g, "Please do")
      .replace(/by any chance/g, "")
      .replace(/maybe/g, "")
      .replace(/perhaps/g, "")
      .replace(/It could be ~/g, "It is ~")
      .replace(/You can ~/g, "You do ~");
  }

  // Gentle style - friendly and polite
  else if (style === "gentle") {
    transformed = transformed
      .replace(/Please do/g, "I would appreciate it if you could do it")
      .replace(/Please do\./g, "I would appreciate it if you could do it.")
      .replace(/Could I\?/g, "Could you please?")
      .replace(/a little/g, "I ask of you")
      .replace(/It is ~/g, "It seems to be ~")
      .replace(/I do ~/g, "It seems to be ~");
  }

  // Neutral style - balanced expression
  else if (style === "neutral") {
    transformed = transformed
      .replace(/Please do/g, "I ask of you")
      .replace(/Could I\?/g, "Could you please?")
      .replace(/a little/g, "I ask of you")
      .replace(/Please do/g, "I would appreciate it if you could do it")
      .replace(/~입니다/g, "~입니다")
      .replace(/~합니다/g, "~합니다");
  }

  // Adjustment based on formality level
  if (adjustedFormality >= 8) {
    transformed = transformed
      .replace(/Please do/g, "I hope you will do it")
      .replace(/I ask of you/g, "I will ask of you")
      .replace(/I would appreciate it/g, "I will appreciate it")
      .replace(/It is ~/g, "It is ~ (very formal)")
      .replace(/I do ~/g, "I do ~ (very formal)");
  } else if (adjustedFormality <= 3) {
    transformed = transformed
      .replace(/I hope you will do it/g, "Please do")
      .replace(/I will ask of you/g, "I ask of you")
      .replace(/I will appreciate it/g, "Thank you")
      .replace(/It is ~ (very formal)/g, "It is ~ (less formal)")
      .replace(/I do ~ (very formal)/g, "I do ~ (less formal)");
  }

  // Adjustment based on friendliness level
  if (adjustedFriendliness >= 8) {
    transformed = transformed
      .replace(/~/g, "~")
      .replace(/\./g, "~")
      .replace(/~/g, "~");
  }

  // Adjustment based on emotion expression level
  if (adjustedEmotion >= 8) {
    transformed = transformed.replace(/~/g, "~").replace(/~/g, "~");
  }

  return transformed;
};

export const generateMockConversion = (
  inputText: string,
  context: ConversionContext,
  userProfile: UserProfile
): ConversionResponse => {
  const baseFormality = userProfile.baseFormalityLevel;
  const baseFriendliness = userProfile.baseFriendlinessLevel;
  const baseEmotion = userProfile.baseEmotionLevel;

  const adjustment = CONTEXT_ADJUSTMENTS[context];

  const adjustedFormality = Math.max(
    0,
    Math.min(10, baseFormality + adjustment.formality)
  );
  const adjustedFriendliness = Math.max(
    0,
    Math.min(10, baseFriendliness + adjustment.friendliness)
  );
  const adjustedEmotion = Math.max(
    0,
    Math.min(10, baseEmotion + adjustment.emotion)
  );

  return {
    conversionId: Date.now(),
    versions: {
      direct: transformText(inputText, "direct", adjustedFormality, adjustedFriendliness, adjustedEmotion),
      gentle: transformText(inputText, "gentle", adjustedFormality, adjustedFriendliness, adjustedEmotion),
      neutral: transformText(inputText, "neutral", adjustedFormality, adjustedFriendliness, adjustedEmotion),
    },
    analysis: {
      formalityLevel: adjustedFormality,
      friendlinessLevel: adjustedFriendliness,
      emotionLevel: adjustedEmotion,
    },
  };
};
