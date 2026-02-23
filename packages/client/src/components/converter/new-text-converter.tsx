// NewTextConverter.tsx
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import {
  ArrowRightLeft,
  Copy,
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  Sparkles,
  BarChart3,
  Settings,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import type { UserProfile } from "@shared/schema";
import { API } from "@/lib/endpoints";

interface ConversionResponse {
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

interface NewTextConverterProps {
  userProfile: UserProfile;
  userId: string;
}

// Temporary mock conversion data generation function
const generateMockConversion = (
  inputText: string,
  context: string,
  userProfile: UserProfile
): ConversionResponse => {
  const baseFormality = userProfile.baseFormalityLevel;
  const baseFriendliness = userProfile.baseFriendlinessLevel;
  const baseEmotion = userProfile.baseEmotionLevel;

  // Style adjustment based on context
  const contextAdjustments = {
    general: { formality: 0, friendliness: 0, emotion: 0 },
    report: { formality: 2, friendliness: -1, emotion: -1 },
    education: { formality: 1, friendliness: 1, emotion: 0 },
    social: { formality: -2, friendliness: 2, emotion: 1 },
  };

  const adjustment =
    contextAdjustments[context as keyof typeof contextAdjustments] ||
    contextAdjustments.general;

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

  // Actual text conversion logic
  const transformText = (
    text: string,
    style: "direct" | "gentle" | "neutral"
  ) => {
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

  return {
    conversionId: Date.now(),
    versions: {
      direct: transformText(inputText, "direct"),
      gentle: transformText(inputText, "gentle"),
      neutral: transformText(inputText, "neutral"),
    },
    analysis: {
      formalityLevel: adjustedFormality,
      friendlinessLevel: adjustedFriendliness,
      emotionLevel: adjustedEmotion,
    },
  };
};

export default function NewTextConverter({
  userProfile,
  userId,
}: NewTextConverterProps) {
  const [inputText, setInputText] = useState("");
  const [context, setContext] = useState<
    "general" | "report" | "education" | "social"
  >("general");
  const [lastConversionId, setLastConversionId] = useState<number | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<
    "direct" | "gentle" | "neutral" | null
  >(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [negativePreferences, setNegativePreferences] = useState({
    rhetoricLevel: "moderate",
    repetitionTolerance: "moderate",
    punctuationStyle: "standard",
    contentFocus: "balanced",
    bulletPreference: "minimal",
    emoticonPolicy: "contextual",
  });
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const convertMutation = useMutation({
    mutationFn: async (): Promise<ConversionResponse> => {
      const isFinetune = context === "report";
      const url = isFinetune ? API.finetune.convert : API.conversion;

      const requestBody = {
        // text: inputText.trim(),
        // user_profile: userProfile || {
        //   baseFormalityLevel: 3,
        //   baseFriendlinessLevel: 3,
        //   baseEmotionLevel: 3,
        //   baseDirectnessLevel: 3,
        // },
        // context: context,
        // negative_preferences: negativePreferences,
        // ...(isFinetune && { force_convert: false }),
        text: inputText.trim(),
        context: context,
        userId: userId,
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
            // Keep analysis information based on profile
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

      if (convertedData.conversionId)
        setLastConversionId(convertedData.conversionId);
      return convertedData;
    },
    onSuccess: (data) => {
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
      selectedVersion: "direct" | "gentle" | "neutral";
      userFeedback?: string;
    }) => {
      // Save to localStorage instead of backend API
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

  const handleVersionSelect = (
    version: "direct" | "gentle" | "neutral",
    feedback?: string
  ) => {
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

  const getContextLabel = (
    ctx: "general" | "report" | "education" | "social"
  ) => {
    const labels = {
      general: "General",
      report: "Report/Document",
      education: "Education/Explanation",
      social: "Social Media",
    } as const;
    return labels[ctx];
  };

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ArrowRightLeft className="w-5 h-5" />
            Text Conversion
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="Enter the text to convert..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            className="min-h-[120px]"
          />

          <div className="flex items-end gap-4">
            <div className="flex-1">
              <label className="block mb-2 text-sm font-medium">
                Conversion Context
              </label>
              <Select
                value={context}
                onValueChange={(
                  value: "general" | "report" | "education" | "social"
                ) => setContext(value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="general">General</SelectItem>
                  <SelectItem value="report">Report/Document</SelectItem>
                  <SelectItem value="education">
                    Education/Explanation
                  </SelectItem>
                  <SelectItem value="social">Social Media</SelectItem>
                </SelectContent>
              </Select>
              {context === "report" && (
                <div className="mt-1 text-xs text-blue-600">
                  Report/Official Document mode uses a specialized fine-tuning
                  model to provide a single optimized result.
                </div>
              )}
            </div>

            <Button
              onClick={handleConvert}
              disabled={convertMutation.isPending}
              className="min-w-[120px]"
            >
              {convertMutation.isPending ? (
                <>
                  <Sparkles className="w-4 h-4 mr-2 animate-spin" />
                  Converting...
                </>
              ) : (
                <>
                  <ArrowRightLeft className="w-4 h-4 mr-2" />
                  Convert
                </>
              )}
            </Button>
          </div>

          {/* Advanced Settings Toggle */}
          <div className="pt-4 border-t">
            <Button
              variant="ghost"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="justify-between w-full p-2"
            >
              <span className="flex items-center gap-2">
                <Settings className="w-4 h-4" />
                Advanced Settings (Negative Prompts)
              </span>
              {showAdvanced ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </Button>

            {showAdvanced && (
              <div className="p-4 mt-4 space-y-4 rounded-lg bg-gray-50">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="block mb-2 text-sm font-medium">
                      Rhetoric Level
                    </label>
                    <Select
                      value={negativePreferences.rhetoricLevel}
                      onValueChange={(value) =>
                        setNegativePreferences({
                          ...negativePreferences,
                          rhetoricLevel: value,
                        })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="moderate">Moderate</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="block mb-2 text-sm font-medium">
                      Repetition Tolerance
                    </label>
                    <Select
                      value={negativePreferences.repetitionTolerance}
                      onValueChange={(value) =>
                        setNegativePreferences({
                          ...negativePreferences,
                          repetitionTolerance: value,
                        })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="moderate">Moderate</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="block mb-2 text-sm font-medium">
                      Punctuation Style
                    </label>
                    <Select
                      value={negativePreferences.punctuationStyle}
                      onValueChange={(value) =>
                        setNegativePreferences({
                          ...negativePreferences,
                          punctuationStyle: value,
                        })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="minimal">Minimal</SelectItem>
                        <SelectItem value="standard">Standard</SelectItem>
                        <SelectItem value="expressive">Expressive</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="block mb-2 text-sm font-medium">
                      Content Focus
                    </label>
                    <Select
                      value={negativePreferences.contentFocus}
                      onValueChange={(value) =>
                        setNegativePreferences({
                          ...negativePreferences,
                          contentFocus: value,
                        })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="content">Content-focused</SelectItem>
                        <SelectItem value="balanced">Balanced</SelectItem>
                        <SelectItem value="format">Format-focused</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="block mb-2 text-sm font-medium">
                      Bullet Points
                    </label>
                    <Select
                      value={negativePreferences.bulletPreference}
                      onValueChange={(value) =>
                        setNegativePreferences({
                          ...negativePreferences,
                          bulletPreference: value,
                        })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="avoid">Avoid</SelectItem>
                        <SelectItem value="minimal">Minimal</SelectItem>
                        <SelectItem value="prefer">Prefer</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="block mb-2 text-sm font-medium">
                      Emoticon Policy
                    </label>
                    <Select
                      value={negativePreferences.emoticonPolicy}
                      onValueChange={(value) =>
                        setNegativePreferences({
                          ...negativePreferences,
                          emoticonPolicy: value,
                        })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">None</SelectItem>
                        <SelectItem value="minimal">Minimal</SelectItem>
                        <SelectItem value="contextual">Contextual</SelectItem>
                        <SelectItem value="frequent">Frequent</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="text-xs text-gray-600">
                  Negative prompts help with more accurate conversions by
                  specifying styles for the AI to avoid.
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Conversion Results */}
      {convertMutation.data && (
        <div className="space-y-6">
          {/* Analysis Summary */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Conversion Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {convertMutation.data.analysis.formalityLevel}/10
                  </div>
                  <div className="text-sm text-gray-600">Formality</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {convertMutation.data.analysis.friendlinessLevel}/10
                  </div>
                  <div className="text-sm text-gray-600">Friendliness</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {convertMutation.data.analysis.emotionLevel}/10
                  </div>
                  <div className="text-sm text-gray-600">
                    Emotion Expression
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Version Cards */}
          <div
            className={`grid gap-4 ${context === "report"
              ? "grid-cols-1 max-w-2xl mx-auto"
              : "md:grid-cols-3"
              }`}
          >
            {context === "report" ? (
              /* Single Optimized Version for Report Mode */
              <Card
                className={
                  selectedVersion === "neutral"
                    ? "ring-2 ring-blue-500 bg-blue-50"
                    : ""
                }
              >
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="text-lg">Optimized Official Style</span>
                    <Badge
                      variant="outline"
                      className="text-blue-800 bg-blue-100"
                    >
                      Fine-tuned
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-3 text-sm rounded-lg bg-gray-50">
                    {convertMutation.data.versions.neutral}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      onClick={() => handleVersionSelect("neutral")}
                      className={`flex-1 ${selectedVersion === "neutral"
                        ? "bg-blue-600 hover:bg-blue-700"
                        : ""
                        }`}
                      variant={
                        selectedVersion === "neutral" ? "default" : "default"
                      }
                    >
                      <ThumbsUp
                        className={`w-4 h-4 mr-1 ${selectedVersion === "neutral" ? "fill-current" : ""
                          }`}
                      />
                      {selectedVersion === "neutral" ? "Selected" : "Select"}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() =>
                        handleCopy(convertMutation.data.versions.neutral)
                      }
                    >
                      <Copy className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ) : (
              /* Three Versions for Other Modes */
              <>
                {/* Direct Version */}
                <Card
                  className={
                    selectedVersion === "direct"
                      ? "ring-2 ring-blue-500 bg-blue-50"
                      : ""
                  }
                >
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="text-lg">Direct</span>
                      <Badge variant="outline">Blunt</Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="p-3 text-sm rounded-lg bg-gray-50">
                      {convertMutation.data.versions.direct}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        onClick={() => handleVersionSelect("direct")}
                        className={`flex-1 ${selectedVersion === "direct"
                          ? "bg-blue-600 hover:bg-blue-700"
                          : ""
                          }`}
                        variant={
                          selectedVersion === "direct" ? "default" : "default"
                        }
                      >
                        <ThumbsUp
                          className={`w-4 h-4 mr-1 ${selectedVersion === "direct" ? "fill-current" : ""
                            }`}
                        />
                        {selectedVersion === "direct" ? "Selected" : "Select"}
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() =>
                          handleCopy(convertMutation.data.versions.direct)
                        }
                      >
                        <Copy className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                {/* Gentle Version */}
                <Card
                  className={
                    selectedVersion === "gentle"
                      ? "ring-2 ring-green-500 bg-green-50"
                      : ""
                  }
                >
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="text-lg">Gentle</span>
                      <Badge
                        variant="outline"
                        className="text-green-800 bg-green-100"
                      >
                        Friendly
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="p-3 text-sm rounded-lg bg-gray-50">
                      {convertMutation.data.versions.gentle}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        onClick={() => handleVersionSelect("gentle")}
                        className={`flex-1 ${selectedVersion === "gentle"
                          ? "bg-green-600 hover:bg-green-700"
                          : ""
                          }`}
                        variant={
                          selectedVersion === "gentle" ? "default" : "default"
                        }
                      >
                        <ThumbsUp
                          className={`w-4 h-4 mr-1 ${selectedVersion === "gentle" ? "fill-current" : ""
                            }`}
                        />
                        {selectedVersion === "gentle" ? "Selected" : "Select"}
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() =>
                          handleCopy(convertMutation.data.versions.gentle)
                        }
                      >
                        <Copy className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                {/* Neutral Version */}
                <Card
                  className={
                    selectedVersion === "neutral"
                      ? "ring-2 ring-purple-500 bg-purple-50"
                      : ""
                  }
                >
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="text-lg">Neutral</span>
                      <Badge
                        variant="outline"
                        className="text-blue-800 bg-blue-100"
                      >
                        Balanced
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="p-3 text-sm rounded-lg bg-gray-50">
                      {convertMutation.data.versions.neutral}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        onClick={() => handleVersionSelect("neutral")}
                        className={`flex-1 ${selectedVersion === "neutral"
                          ? "bg-purple-600 hover:bg-purple-700"
                          : ""
                          }`}
                        variant={
                          selectedVersion === "neutral" ? "default" : "default"
                        }
                      >
                        <ThumbsUp
                          className={`w-4 h-4 mr-1 ${selectedVersion === "neutral" ? "fill-current" : ""
                            }`}
                        />
                        {selectedVersion === "neutral" ? "Selected" : "Select"}
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() =>
                          handleCopy(convertMutation.data.versions.neutral)
                        }
                      >
                        <Copy className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
