import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import type { UserProfile } from "@shared/schema";
import { API } from "@/lib/endpoints";
import type {
  ConversionResponse,
  ConversionContext,
  VersionType,
  NegativePreferences,
} from "./types";
import { DEFAULT_NEGATIVE_PREFERENCES } from "./types";

interface UseTextConversionProps {
  userProfile: UserProfile;
  userId: string;
}

export const useTextConversion = ({ userProfile, userId }: UseTextConversionProps) => {
  const [inputText, setInputText] = useState("");
  const [context, setContext] = useState<ConversionContext>("general");
  const [lastConversionId, setLastConversionId] = useState<number | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<VersionType | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [negativePreferences, setNegativePreferences] = useState<NegativePreferences>(
    DEFAULT_NEGATIVE_PREFERENCES
  );
  const { toast } = useToast();

  const convertMutation = useMutation({
    mutationFn: async (): Promise<ConversionResponse> => {
      const isFinetune = context === "report";
      const url = isFinetune ? API.finetune.convert : API.conversion;

      const requestBody = {
        text: inputText.trim(),
        user_profile: userProfile || {
          baseFormalityLevel: 3,
          baseFriendlinessLevel: 3,
          baseEmotionLevel: 3,
          baseDirectnessLevel: 3,
        },
        context: context,
        negative_preferences: negativePreferences,
        ...(isFinetune && { force_convert: false }),
      };

      console.log("Request data to be sent:", requestBody);
      console.log("Negative Preferences:", negativePreferences);

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `API Error: ${response.status}`);
      }

      const result = await response.json();

      let convertedData: ConversionResponse;

      if (isFinetune) {
        const convertedText = result.converted_text || inputText;
        convertedData = {
          conversionId: Date.now(),
          versions: {
            direct: convertedText,
            gentle: convertedText,
            neutral: convertedText,
          },
          analysis: {
            formalityLevel: userProfile.baseFormalityLevel,
            friendlinessLevel: userProfile.baseFriendlinessLevel,
            emotionLevel: userProfile.baseEmotionLevel,
          },
        };
      } else {
        convertedData = {
          conversionId: Date.now(),
          versions: {
            direct: result.converted_texts?.direct || inputText,
            gentle: result.converted_texts?.gentle || inputText,
            neutral: result.converted_texts?.neutral || inputText,
          },
          analysis: {
            formalityLevel: userProfile.baseFormalityLevel,
            friendlinessLevel: userProfile.baseFriendlinessLevel,
            emotionLevel: userProfile.baseEmotionLevel,
          },
        };
      }

      if (convertedData.conversionId) {
        setLastConversionId(convertedData.conversionId);
      }
      return convertedData;
    },
    onSuccess: () => {
      toast({
        title: "Conversion Complete",
        description: "The text has been successfully converted.",
      });
    },
    onError: (error) => {
      toast({
        title: "Conversion Failed",
        description:
          error instanceof Error
            ? error.message
            : "An unknown error has occurred.",
        variant: "destructive",
      });
    },
  });

  const feedbackMutation = useMutation({
    mutationFn: async ({
      selectedVersion,
      userFeedback,
    }: {
      selectedVersion: VersionType;
      userFeedback?: string;
    }) => {
      const feedbackData = {
        conversionId: lastConversionId,
        selectedVersion,
        userFeedback,
        userId,
        timestamp: new Date().toISOString(),
      };

      const existingFeedback = JSON.parse(
        localStorage.getItem("chatToner_feedback") || "[]"
      );
      existingFeedback.push(feedbackData);
      localStorage.setItem(
        "chatToner_feedback",
        JSON.stringify(existingFeedback)
      );

      return { success: true };
    },
    onSuccess: () => {
      toast({
        title: "Feedback Saved",
        description: "The selected version has been saved.",
      });
    },
  });

  const handleConvert = () => {
    if (!inputText.trim()) {
      toast({
        title: "Please enter text",
        description: "Please enter the text to be converted.",
        variant: "destructive",
      });
      return;
    }
    convertMutation.mutate();
  };

  const handleVersionSelect = (version: VersionType, feedback?: string) => {
    setSelectedVersion(version);
    feedbackMutation.mutate({
      selectedVersion: version,
      userFeedback: feedback,
    });
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copy Complete",
      description: "The text has been copied to the clipboard.",
    });
  };

  return {
    // State
    inputText,
    context,
    selectedVersion,
    showAdvanced,
    negativePreferences,
    
    // State setters
    setInputText,
    setContext,
    setShowAdvanced,
    setNegativePreferences,
    
    // Mutations
    convertMutation,
    feedbackMutation,
    
    // Handlers
    handleConvert,
    handleVersionSelect,
    handleCopy,
  };
};
