import { useState, useMemo, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { TransformStyleCard } from "@/components/Organisms/TransformStyleCard";
import { api } from "@/lib/api";
import type { UserProfile } from "@shared/schema";

// Define the analysis result type, adapted from StyleConverter
interface StyleAnalysis {
  directness_score: number;
  softness_score: number;
  politeness_score: number;
  converted_text: string;
  converted_texts?: {
    // Store all converted texts
    direct: string;
    gentle: string;
    neutral: string;
  };
  suggestions: Array<{
    type: "directness" | "softness" | "politeness";
    original: string;
    suggestion: string;
    reason: string;
  }>;
}

// Mock data generation function from StyleConverter
const generateMockAnalysis = (text: string): StyleAnalysis => {
  return {
    directness_score: Math.floor(Math.random() * 50) + 50,
    softness_score: Math.floor(Math.random() * 50) + 50,
    politeness_score: Math.floor(Math.random() * 50) + 50,
    converted_text: text + " (style converted)",
    converted_texts: {
      direct: text + " (direct)",
      gentle: text + " (gentle)",
      neutral: text + " (neutral)",
    },
    suggestions: [
      {
        type: "directness",
        original: "this part",
        suggestion: "that part",
        reason: "Changed to a more direct expression to clarify the meaning.",
      },
      {
        type: "softness",
        original: "do it",
        suggestion: "Could you do it for me?",
        reason: "Changed to a softer expression to give a friendly feeling.",
      },
    ],
  };
};

export default function TransformStylePage() {
  const { toast } = useToast();

  // State for all inputs
  const [inputText, setInputText] = useState("");
  const [selectedStyle, setSelectedStyle] = useState("directness");
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);

  // State for the analysis result from the API
  const [analysis, setAnalysis] = useState<StyleAnalysis | null>(null);

  // Load user profile from localStorage
  useEffect(() => {
    const profileString = localStorage.getItem("chatToner_profile");
    if (profileString) {
      try {
        setUserProfile(JSON.parse(profileString));
      } catch (error) {
        console.error("Failed to parse user profile:", error);
      }
    }
  }, []);

  // Mutation logic adapted from StyleConverter
  const convertMutation = useMutation({
    mutationFn: async ({
      text,
      style,
    }: {
      text: string;
      style: string;
    }): Promise<StyleAnalysis> => {
      // Use actual API call
      console.log(`Transforming text: ${text}`);

      try {
        const result = await api.convertStyle({
          text,
          user_profile: userProfile
            ? {
                baseFormalityLevel: Math.round(
                  userProfile.baseFormalityLevel / 10
                ),
                baseFriendlinessLevel: Math.round(
                  userProfile.baseFriendlinessLevel / 10
                ),
                baseEmotionLevel: Math.round(userProfile.baseEmotionLevel / 10),
                baseDirectnessLevel: Math.round(
                  userProfile.baseDirectnessLevel / 10
                ),
              }
            : {
                baseFormalityLevel: 8,
                baseFriendlinessLevel: 6,
                baseEmotionLevel: 5,
                baseDirectnessLevel: 8,
              },
          context: "general",
        });

        // Transform API response to match StyleAnalysis interface
        console.log("API Response:", result);
        console.log("API Response converted_texts:", result.converted_texts);

        // Store all converted texts from API
        const allConvertedTexts = result.converted_texts || {};

        // Get the default converted text based on selected style for initial display
        let convertedText = text;
        if (allConvertedTexts && typeof allConvertedTexts === "object") {
          if (style === "directness") {
            convertedText = allConvertedTexts.direct || text;
          } else if (style === "softness") {
            convertedText = allConvertedTexts.gentle || text;
          } else if (style === "politeness") {
            convertedText = allConvertedTexts.neutral || text;
          } else {
            convertedText =
              allConvertedTexts.direct ||
              allConvertedTexts.gentle ||
              allConvertedTexts.neutral ||
              text;
          }
        } else {
          console.warn(
            "No converted_texts in API response, using original text"
          );
        }

        console.log("Final converted text:", convertedText);

        return {
          directness_score: 75, // Mock scores since API doesn't return them
          softness_score: 60,
          politeness_score: 70,
          converted_text: convertedText,
          converted_texts: allConvertedTexts, // Store all converted texts
          suggestions: [], // Mock suggestions since API doesn't return them
        };
      } catch (error) {
        console.error("API call failed, falling back to mock data:", error);
        // Fallback to mock data if API fails
        return generateMockAnalysis(text);
      }
    },
    onSuccess: (data) => {
      setAnalysis(data);
      toast({
        title: "Conversion Complete",
        description: "Text style conversion is complete.",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Conversion Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleTransformClick = () => {
    if (isTransformDisabled) return;
    convertMutation.mutate({ text: inputText, style: selectedStyle });
  };

  const isTransformDisabled = !inputText.trim() || convertMutation.isPending;

  // Logic to format the output text based on the selected style
  const outputValue = useMemo(() => {
    if (convertMutation.isPending) return "Transforming...";
    if (!analysis) return "Transformed text will appear here";

    // Get the converted text based on selected style
    let displayText = analysis.converted_text;

    if (analysis.converted_texts) {
      if (selectedStyle === "directness" && analysis.converted_texts.direct) {
        displayText = analysis.converted_texts.direct;
      } else if (
        selectedStyle === "softness" &&
        analysis.converted_texts.gentle
      ) {
        displayText = analysis.converted_texts.gentle;
      } else if (
        selectedStyle === "politeness" &&
        analysis.converted_texts.neutral
      ) {
        displayText = analysis.converted_texts.neutral;
      }
    }

    const outputLines = [];
    outputLines.push(`[Converted Text]`);
    outputLines.push(displayText);

    const relevantSuggestions = analysis.suggestions.filter(
      (s) => s.type === selectedStyle
    );

    // Only show suggestions section if there are actual suggestions
    if (relevantSuggestions.length > 0) {
      outputLines.push("");
      outputLines.push(`[Suggestions for ${selectedStyle}]`);
      const suggestionLines = relevantSuggestions.map(
        (s) => `- "${s.original}" -> "${s.suggestion}" (${s.reason})`
      );
      outputLines.push(...suggestionLines);
    }

    return outputLines.join("\n");
  }, [analysis, selectedStyle, convertMutation.isPending]);

  return (
    <div>
      <h1 className="font-bold text-black text-7xl">Transform Style</h1>
      <p className="mt-4 mb-12 text-5xl font-medium text-gray-700">
        Convert text to your team's unique style profile.
      </p>
      <div className="flex justify-center">
        <TransformStyleCard
          inputValue={inputText}
          onInputChange={setInputText}
          selectedStyleValue={selectedStyle}
          onSelectedStyleChange={setSelectedStyle}
          outputValue={outputValue}
          onTransformClick={handleTransformClick}
          isTransformDisabled={isTransformDisabled}
        />
      </div>
    </div>
  );
}
