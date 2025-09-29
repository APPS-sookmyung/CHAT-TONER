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
        .replace(/할 수 있을까요\?/g, "해주세요.")
        .replace(/해주시면 감사하겠습니다/g, "해주세요")
        .replace(/부탁드립니다/g, "해주세요")
        .replace(/좀/g, "")
        .replace(/해주실 수 있나요/g, "해주세요")
        .replace(/혹시/g, "")
        .replace(/아마도/g, "")
        .replace(/어쩌면/g, "")
        .replace(/~일 수도 있습니다/g, "~입니다")
        .replace(/~할 수도 있습니다/g, "~합니다");
    }

    // Gentle style - friendly and polite
    else if (style === "gentle") {
      transformed = transformed
        .replace(/해주세요/g, "해주시면 감사하겠습니다")
        .replace(/해주세요\./g, "해주시면 감사하겠습니다.")
        .replace(/할 수 있을까요\?/g, "해주실 수 있을까요?")
        .replace(/좀/g, "부탁드려요")
        .replace(/해주세요/g, "해주시면 정말 감사하겠습니다")
        .replace(/~입니다/g, "~일 것 같습니다")
        .replace(/~합니다/g, "~할 것 같습니다")
        .replace(/~해요/g, "~하시는 것 같아요");
    }

    // Neutral style - balanced expression
    else if (style === "neutral") {
      transformed = transformed
        .replace(/해주세요/g, "부탁드립니다")
        .replace(/할 수 있을까요\?/g, "해주실 수 있을까요?")
        .replace(/좀/g, "부탁드립니다")
        .replace(/해주세요/g, "해주시면 감사하겠습니다")
        .replace(/~입니다/g, "~입니다")
        .replace(/~합니다/g, "~합니다");
    }

    // Adjustment based on formality level
    if (adjustedFormality >= 8) {
      transformed = transformed
        .replace(/해주세요/g, "해주시기 바랍니다")
        .replace(/부탁드립니다/g, "부탁드리겠습니다")
        .replace(/감사하겠습니다/g, "감사드리겠습니다")
        .replace(/~입니다/g, "~이옵니다")
        .replace(/~합니다/g, "~하옵니다");
    } else if (adjustedFormality <= 3) {
      transformed = transformed
        .replace(/해주시기 바랍니다/g, "해주세요")
        .replace(/부탁드리겠습니다/g, "부탁드려요")
        .replace(/감사드리겠습니다/g, "감사해요")
        .replace(/~이옵니다/g, "~이에요")
        .replace(/~하옵니다/g, "~해요");
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

      console.log("전송할 요청 데이터:", requestBody);
      console.log("네거티브 프리퍼런스:", negativePreferences);

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
        title: "변환 완료",
        description: "텍스트가 성공적으로 변환되었습니다.",
      });
    },
    onError: (error) => {
      toast({
        title: "변환 실패",
        description:
          error instanceof Error
            ? error.message
            : "알 수 없는 오류가 발생했습니다.",
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
        title: "피드백 저장 완료",
        description: "선택한 버전이 저장되었습니다.",
      });
    },
  });

  const handleConvert = () => {
    if (!inputText.trim()) {
      toast({
        title: "텍스트를 입력해주세요",
        description: "변환할 텍스트를 입력해주세요.",
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
      title: "복사 완료",
      description: "텍스트가 클립보드에 복사되었습니다.",
    });
  };

  const getContextLabel = (
    ctx: "general" | "report" | "education" | "social"
  ) => {
    const labels = {
      general: "일반",
      report: "보고서/문서",
      education: "교육/설명",
      social: "소셜미디어",
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
            텍스트 변환
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="변환할 텍스트를 입력하세요..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            className="min-h-[120px]"
          />

          <div className="flex items-end gap-4">
            <div className="flex-1">
              <label className="block mb-2 text-sm font-medium">
                변환 컨텍스트
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
                  <SelectItem value="general">일반</SelectItem>
                  <SelectItem value="report">보고서/문서</SelectItem>
                  <SelectItem value="education">교육/설명</SelectItem>
                  <SelectItem value="social">소셜미디어</SelectItem>
                </SelectContent>
              </Select>
              {context === "report" && (
                <div className="mt-1 text-xs text-blue-600">
                  보고서/공문 모드는 특화된 파인튜닝 모델을 사용하여 단일 최적화
                  결과를 제공합니다.
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
                  변환 중...
                </>
              ) : (
                <>
                  <ArrowRightLeft className="w-4 h-4 mr-2" />
                  변환하기
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
                고급 설정 (네거티브 프롬프트)
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
                      수사법 수준
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
                        <SelectItem value="low">낮음</SelectItem>
                        <SelectItem value="moderate">보통</SelectItem>
                        <SelectItem value="high">높음</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="block mb-2 text-sm font-medium">
                      반복 허용도
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
                        <SelectItem value="low">낮음</SelectItem>
                        <SelectItem value="moderate">보통</SelectItem>
                        <SelectItem value="high">높음</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="block mb-2 text-sm font-medium">
                      문장부호 스타일
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
                        <SelectItem value="minimal">최소화</SelectItem>
                        <SelectItem value="standard">표준</SelectItem>
                        <SelectItem value="expressive">표현력</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="block mb-2 text-sm font-medium">
                      내용 초점
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
                        <SelectItem value="content">내용 중심</SelectItem>
                        <SelectItem value="balanced">균형</SelectItem>
                        <SelectItem value="format">형식 중심</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="block mb-2 text-sm font-medium">
                      불릿 포인트
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
                        <SelectItem value="avoid">피하기</SelectItem>
                        <SelectItem value="minimal">최소한</SelectItem>
                        <SelectItem value="prefer">선호</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="block mb-2 text-sm font-medium">
                      이모티콘 정책
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
                        <SelectItem value="none">사용 안함</SelectItem>
                        <SelectItem value="minimal">최소한</SelectItem>
                        <SelectItem value="contextual">상황에 맞게</SelectItem>
                        <SelectItem value="frequent">자주 사용</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="text-xs text-gray-600">
                  네거티브 프롬프트는 AI가 피해야 할 스타일을 지정하여 더 정확한
                  변환을 도와줍니다.
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
                변환 분석
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {convertMutation.data.analysis.formalityLevel}/10
                  </div>
                  <div className="text-sm text-gray-600">정중함</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {convertMutation.data.analysis.friendlinessLevel}/10
                  </div>
                  <div className="text-sm text-gray-600">친근함</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {convertMutation.data.analysis.emotionLevel}/10
                  </div>
                  <div className="text-sm text-gray-600">감정 표현</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Version Cards */}
          <div
            className={`grid gap-4 ${
              context === "report"
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
                    <span className="text-lg">최적화된 공문체</span>
                    <Badge
                      variant="outline"
                      className="text-blue-800 bg-blue-100"
                    >
                      파인튜닝
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
                      className={`flex-1 ${
                        selectedVersion === "neutral"
                          ? "bg-blue-600 hover:bg-blue-700"
                          : ""
                      }`}
                      variant={
                        selectedVersion === "neutral" ? "default" : "default"
                      }
                    >
                      <ThumbsUp
                        className={`w-4 h-4 mr-1 ${
                          selectedVersion === "neutral" ? "fill-current" : ""
                        }`}
                      />
                      {selectedVersion === "neutral" ? "선택됨" : "선택"}
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
                      <span className="text-lg">직접적</span>
                      <Badge variant="outline">직설적</Badge>
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
                        className={`flex-1 ${
                          selectedVersion === "direct"
                            ? "bg-blue-600 hover:bg-blue-700"
                            : ""
                        }`}
                        variant={
                          selectedVersion === "direct" ? "default" : "default"
                        }
                      >
                        <ThumbsUp
                          className={`w-4 h-4 mr-1 ${
                            selectedVersion === "direct" ? "fill-current" : ""
                          }`}
                        />
                        {selectedVersion === "direct" ? "선택됨" : "선택"}
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
                      <span className="text-lg">부드러운</span>
                      <Badge
                        variant="outline"
                        className="text-green-800 bg-green-100"
                      >
                        친근
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
                        className={`flex-1 ${
                          selectedVersion === "gentle"
                            ? "bg-green-600 hover:bg-green-700"
                            : ""
                        }`}
                        variant={
                          selectedVersion === "gentle" ? "default" : "default"
                        }
                      >
                        <ThumbsUp
                          className={`w-4 h-4 mr-1 ${
                            selectedVersion === "gentle" ? "fill-current" : ""
                          }`}
                        />
                        {selectedVersion === "gentle" ? "선택됨" : "선택"}
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
                      <span className="text-lg">중립적</span>
                      <Badge
                        variant="outline"
                        className="text-blue-800 bg-blue-100"
                      >
                        균형
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
                        className={`flex-1 ${
                          selectedVersion === "neutral"
                            ? "bg-purple-600 hover:bg-purple-700"
                            : ""
                        }`}
                        variant={
                          selectedVersion === "neutral" ? "default" : "default"
                        }
                      >
                        <ThumbsUp
                          className={`w-4 h-4 mr-1 ${
                            selectedVersion === "neutral" ? "fill-current" : ""
                          }`}
                        />
                        {selectedVersion === "neutral" ? "선택됨" : "선택"}
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
