"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import type { UserProfile } from "@shared/schema";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Zap,
  Feather,
  Hand,
  Wand2,
  CheckCircle,
  Lightbulb,
  Copy,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface StyleConverterProps {
  userProfile: UserProfile;
}

interface StyleAnalysis {
  directness_score: number;
  softness_score: number;
  politeness_score: number;
  converted_text: string;
  suggestions: Array<{
    type: "directness" | "softness" | "politeness";
    original: string;
    suggestion: string;
    reason: string;
  }>;
}

// Temporary mock data generation function
const generateMockAnalysis = (text: string): StyleAnalysis => {
  return {
    directness_score: Math.floor(Math.random() * 50) + 50,
    softness_score: Math.floor(Math.random() * 50) + 50,
    politeness_score: Math.floor(Math.random() * 50) + 50,
    converted_text: text + " (스타일 변환됨)",
    suggestions: [
      {
        type: "directness",
        original: "이 부분",
        suggestion: "저 부분",
        reason: "더 직접적인 표현으로 변경하여 의미를 명확히 합니다.",
      },
      {
        type: "softness",
        original: "하세요",
        suggestion: "해주시겠어요?",
        reason: "더 부드러운 표현으로 변경하여 친근한 느낌을 줍니다.",
      },
      {
        type: "politeness",
        original: "야",
        suggestion: "님",
        reason: "더 정중한 표현으로 변경하여 예의를 갖춥니다.",
      },
    ],
  };
};

export default function StyleConverter({ userProfile }: StyleConverterProps) {
  const [inputText, setInputText] = useState("");
  const [analysis, setAnalysis] = useState<StyleAnalysis | null>(null);
  const { toast } = useToast();

  const convertMutation = useMutation({
    mutationFn: async (text: string): Promise<StyleAnalysis> => {
      // TODO: Replace with actual style conversion API call logic.
      // const { rag } = await import("@/lib/rag");
      // const result = await rag.convertText({ query: text, user_profile: userProfile });

      // Currently returns mock data after 2 seconds.
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve(generateMockAnalysis(text));
        }, 2000);
      });
    },
    onSuccess: (data) => {
      setAnalysis(data);
      toast({
        title: "변환 완료",
        description: "텍스트 스타일 변환이 완료되었습니다.",
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

  const handleConvert = () => {
    if (!inputText.trim()) {
      toast({
        title: "텍스트를 입력해주세요",
        description: "변환할 텍스트를 입력해주세요.",
        variant: "destructive",
      });
      return;
    }
    convertMutation.mutate(inputText.trim());
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "복사 완료",
      description: "텍스트가 클립보드에 복사되었습니다.",
    });
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-blue-600";
    if (score >= 40) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreBadge = (score: number) => {
    if (score >= 80)
      return <Badge className="bg-green-100 text-green-800">매우 높음</Badge>;
    if (score >= 60)
      return <Badge className="bg-blue-100 text-blue-800">높음</Badge>;
    if (score >= 40)
      return <Badge className="bg-yellow-100 text-yellow-800">보통</Badge>;
    return <Badge className="bg-red-100 text-red-800">낮음</Badge>;
  };

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wand2 className="w-5 h-5" />
            변환할 텍스트
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="스타일을 변환할 텍스트를 입력하세요...\n당신의 프로필에 맞춰 새로운 스타일로 변환해 드립니다."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            className="min-h-[150px]"
          />
          <Button
            onClick={handleConvert}
            disabled={convertMutation.isPending}
            className="w-full"
          >
            {convertMutation.isPending ? "변환 중..." : "스타일 변환"}
          </Button>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysis && (
        <div className="space-y-6">
          {/* Converted Text Display */}
          <Card className="bg-gradient-to-br from-white to-sky-50/30 border-sky-100/50 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sky-700">
                <CheckCircle className="w-5 h-5" />
                변환된 텍스트
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-sky-50 rounded-lg p-4 border border-sky-200">
                <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                  {analysis.converted_text}
                </p>
              </div>
              <div className="flex gap-2 mt-4">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => copyToClipboard(analysis.converted_text!)}
                  className="hover:bg-gradient-to-r hover:from-sky-50 hover:to-blue-50 hover:border-sky-300 transition-all duration-300"
                >
                  <Copy className="w-4 h-4 mr-2" />
                  복사하기
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Score Cards */}
          <div className="grid md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-6 text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Zap className="w-5 h-5 text-red-600" />
                  <h3 className="font-semibold">직접성</h3>
                </div>
                <div
                  className={`text-3xl font-bold ${getScoreColor(
                    analysis.directness_score
                  )}`}
                >
                  {Math.round(analysis.directness_score)}
                </div>
                <div className="text-sm text-gray-600">/ 100</div>
                {getScoreBadge(analysis.directness_score)}
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Feather className="w-5 h-5 text-green-600" />
                  <h3 className="font-semibold">부드러움</h3>
                </div>
                <div
                  className={`text-3xl font-bold ${getScoreColor(
                    analysis.softness_score
                  )}`}
                >
                  {Math.round(analysis.softness_score)}
                </div>
                <div className="text-sm text-gray-600">/ 100</div>
                {getScoreBadge(analysis.softness_score)}
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Hand className="w-5 h-5 text-blue-600" />
                  <h3 className="font-semibold">정중함</h3>
                </div>
                <div
                  className={`text-3xl font-bold ${getScoreColor(
                    analysis.politeness_score
                  )}`}
                >
                  {Math.round(analysis.politeness_score)}
                </div>
                <div className="text-sm text-gray-600">/ 100</div>
                {getScoreBadge(analysis.politeness_score)}
              </CardContent>
            </Card>
          </div>

          {/* Suggestions */}
          {analysis.suggestions.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="w-5 h-5" />
                  스타일 개선 제안 ({analysis.suggestions.length}개)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analysis.suggestions.map((suggestion, index) => (
                    <div
                      key={index}
                      className="border border-gray-200 rounded-lg p-4"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <Badge variant="outline" className="capitalize">
                          {suggestion.type}
                        </Badge>
                      </div>
                      <div className="space-y-2">
                        <div>
                          <span className="text-sm text-gray-600">원문: </span>
                          <span className="text-gray-800">
                            {suggestion.original}
                          </span>
                        </div>
                        <div>
                          <span className="text-sm text-gray-600">제안: </span>
                          <span className="text-green-600 font-medium">
                            {suggestion.suggestion}
                          </span>
                        </div>
                        <div>
                          <span className="text-sm text-gray-600">이유: </span>
                          <span className="text-gray-700">
                            {suggestion.reason}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
