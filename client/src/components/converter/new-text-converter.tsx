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
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import type { UserProfile } from "@shared/schema";
import { API } from '@/lib/endpoints';

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

// 임시 모의 변환 데이터 생성 함수
const generateMockConversion = (inputText: string, context: string, userProfile: UserProfile): ConversionResponse => {
  const baseFormality = userProfile.baseFormalityLevel;
  const baseFriendliness = userProfile.baseFriendlinessLevel;
  const baseEmotion = userProfile.baseEmotionLevel;

  // 컨텍스트에 따른 스타일 조정
  const contextAdjustments = {
    general: { formality: 0, friendliness: 0, emotion: 0 },
    report: { formality: 2, friendliness: -1, emotion: -1 },
    education: { formality: 1, friendliness: 1, emotion: 0 },
    social: { formality: -2, friendliness: 2, emotion: 1 }
  };

  const adjustment = contextAdjustments[context as keyof typeof contextAdjustments] || contextAdjustments.general;

  const adjustedFormality = Math.max(0, Math.min(10, baseFormality + adjustment.formality));
  const adjustedFriendliness = Math.max(0, Math.min(10, baseFriendliness + adjustment.friendliness));
  const adjustedEmotion = Math.max(0, Math.min(10, baseEmotion + adjustment.emotion));

  // 실제 텍스트 변환 로직
  const transformText = (text: string, style: 'direct' | 'gentle' | 'neutral') => {
    let transformed = text;
    
    // 직접적 스타일 - 간결하고 명확하게
    if (style === 'direct') {
      transformed = transformed
        .replace(/할 수 있을까요\?/g, '해주세요.')
        .replace(/해주시면 감사하겠습니다/g, '해주세요')
        .replace(/부탁드립니다/g, '해주세요')
        .replace(/좀/g, '')
        .replace(/해주실 수 있나요/g, '해주세요')
        .replace(/혹시/g, '')
        .replace(/아마도/g, '')
        .replace(/어쩌면/g, '')
        .replace(/~일 수도 있습니다/g, '~입니다')
        .replace(/~할 수도 있습니다/g, '~합니다');
    }
    
    // 부드러운 스타일 - 친근하고 공손하게
    else if (style === 'gentle') {
      transformed = transformed
        .replace(/해주세요/g, '해주시면 감사하겠습니다')
        .replace(/해주세요\./g, '해주시면 감사하겠습니다.')
        .replace(/할 수 있을까요\?/g, '해주실 수 있을까요?')
        .replace(/좀/g, '부탁드려요')
        .replace(/해주세요/g, '해주시면 정말 감사하겠습니다')
        .replace(/~입니다/g, '~일 것 같습니다')
        .replace(/~합니다/g, '~할 것 같습니다')
        .replace(/~해요/g, '~하시는 것 같아요');
    }
    
    // 중립적 스타일 - 균형잡힌 표현
    else if (style === 'neutral') {
      transformed = transformed
        .replace(/해주세요/g, '부탁드립니다')
        .replace(/할 수 있을까요\?/g, '해주실 수 있을까요?')
        .replace(/좀/g, '부탁드립니다')
        .replace(/해주세요/g, '해주시면 감사하겠습니다')
        .replace(/~입니다/g, '~입니다')
        .replace(/~합니다/g, '~합니다');
    }

    // 격식도에 따른 조정
    if (adjustedFormality >= 8) {
      transformed = transformed
        .replace(/해주세요/g, '해주시기 바랍니다')
        .replace(/부탁드립니다/g, '부탁드리겠습니다')
        .replace(/감사하겠습니다/g, '감사드리겠습니다')
        .replace(/~입니다/g, '~이옵니다')
        .replace(/~합니다/g, '~하옵니다');
    } else if (adjustedFormality <= 3) {
      transformed = transformed
        .replace(/해주시기 바랍니다/g, '해주세요')
        .replace(/부탁드리겠습니다/g, '부탁드려요')
        .replace(/감사드리겠습니다/g, '감사해요')
        .replace(/~이옵니다/g, '~이에요')
        .replace(/~하옵니다/g, '~해요');
    }

    // 친근함에 따른 조정
    if (adjustedFriendliness >= 8) {
      transformed = transformed
        .replace(/~/g, '~')
        .replace(/\./g, '~')
        .replace(/~/g, '~');
    }

    // 감정 표현에 따른 조정
    if (adjustedEmotion >= 8) {
      transformed = transformed
        .replace(/~/g, '~')
        .replace(/~/g, '~');
    }

    return transformed;
  };

  return {
    conversionId: Date.now(),
    versions: {
      direct: transformText(inputText, 'direct'),
      gentle: transformText(inputText, 'gentle'),
      neutral: transformText(inputText, 'neutral')
    },
    analysis: {
      formalityLevel: adjustedFormality,
      friendlinessLevel: adjustedFriendliness,
      emotionLevel: adjustedEmotion
    }
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
          baseDirectnessLevel: 3
        },
        context: context,
        ...(isFinetune && { force_convert: false }),
      };

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `API Error: ${response.status}`);
      }

      const result = await response.json();
      
      let convertedData: ConversionResponse;

      if (isFinetune) {
        convertedData = {
          conversionId: Date.now(),
          versions: {
            direct: inputText, // 파인튜닝은 단일 결과만 반환하므로 원본 텍스트를 대체 표시
            gentle: inputText,
            neutral: result.converted_text || inputText,
          },
          analysis: { // 분석 정보는 프로필 기반으로 유지
            formalityLevel: userProfile.baseFormalityLevel,
            friendlinessLevel: userProfile.baseFriendlinessLevel,
            emotionLevel: userProfile.baseEmotionLevel,
          }
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
          }
        };
      }

      if (convertedData.conversionId) setLastConversionId(convertedData.conversionId);
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
      // 백엔드 API 대신 로컬 스토리지에 저장
      const feedbackData = {
        conversionId: lastConversionId,
        selectedVersion,
        userFeedback,
        userId,
        timestamp: new Date().toISOString()
      };
      
      const existingFeedback = JSON.parse(localStorage.getItem('chatToner_feedback') || '[]');
      existingFeedback.push(feedbackData);
      localStorage.setItem('chatToner_feedback', JSON.stringify(existingFeedback));
      
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

          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="text-sm font-medium mb-2 block">
                변환 컨텍스트
              </label>
              <Select
                value={context}
                onValueChange={(value: "general" | "report" | "education" | "social") =>
                  setContext(value)
                }
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
              <div className="grid md:grid-cols-3 gap-4">
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
          <div className="grid md:grid-cols-3 gap-4">
            {/* Direct Version */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="text-lg">직접적</span>
                  <Badge variant="outline">직설적</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-gray-50 rounded-lg p-3 text-sm">
                  {convertMutation.data.versions.direct}
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    onClick={() => handleVersionSelect("direct")}
                    className="flex-1"
                  >
                    <ThumbsUp className="w-4 h-4 mr-1" />
                    선택
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleCopy(convertMutation.data.versions.direct)}
                  >
                    <Copy className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Gentle Version */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="text-lg">부드러운</span>
                  <Badge variant="outline" className="bg-green-100 text-green-800">친근</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-gray-50 rounded-lg p-3 text-sm">
                  {convertMutation.data.versions.gentle}
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    onClick={() => handleVersionSelect("gentle")}
                    className="flex-1"
                  >
                    <ThumbsUp className="w-4 h-4 mr-1" />
                    선택
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleCopy(convertMutation.data.versions.gentle)}
                  >
                    <Copy className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Neutral Version */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="text-lg">중립적</span>
                  <Badge variant="outline" className="bg-blue-100 text-blue-800">균형</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-gray-50 rounded-lg p-3 text-sm">
                  {convertMutation.data.versions.neutral}
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    onClick={() => handleVersionSelect("neutral")}
                    className="flex-1"
                  >
                    <ThumbsUp className="w-4 h-4 mr-1" />
                    선택
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleCopy(convertMutation.data.versions.neutral)}
                  >
                    <Copy className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
