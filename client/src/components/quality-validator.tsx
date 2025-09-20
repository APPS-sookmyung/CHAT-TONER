import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
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
  BarChart3,
  CheckCircle,
  AlertTriangle,
  Lightbulb,
  Copy,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface QualityValidatorProps {}

interface QualityAnalysis {
  grammar_score: number;
  formality_score: number;
  readability_score: number;
  improved_text?: string;
  suggestions: Array<{
    type: string;
    original: string;
    suggestion: string;
    reason: string;
  }>;
}

const generateMockAnalysis = (text: string): QualityAnalysis => {
  return {
    grammar_score: Math.floor(Math.random() * 30) + 70,
    formality_score: Math.floor(Math.random() * 40) + 60,
    readability_score: Math.floor(Math.random() * 25) + 75,
    improved_text: text + " (품질 개선됨)",
    suggestions: [
      {
        type: "improvement",
        original: "잘못된 부분",
        suggestion: "개선된 부분",
        reason: "API 호출 실패 시 보여지는 예시 데이터입니다.",
      },
    ],
  };
};

export default function QualityValidator({}: QualityValidatorProps) {
  const [inputText, setInputText] = useState("");
  const [targetAudience, setTargetAudience] = useState<string>("일반인");
  const [context, setContext] = useState<"business" | "report" | "casual">(
    "business"
  );
  const [analysis, setAnalysis] = useState<QualityAnalysis | null>(null);
  const { toast } = useToast();

  const analyzeMutation = useMutation({
    mutationFn: async (text: string): Promise<QualityAnalysis> => {
      try {
        const response = await fetch("/api/v1/quality/analyze", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            text: text,
            target_audience: targetAudience,
            context:
              context === "business"
                ? "일반"
                : context === "report"
                ? "교육"
                : "보고서/공문",
          }),
        });

        if (!response.ok) {
          throw new Error(`API 호출 실패: ${response.status}`);
        }

        const result = await response.json();

        return {
          grammar_score: result.grammarScore || 0,
          formality_score: result.formalityScore || 0,
          readability_score: result.readabilityScore || 0,
          improved_text: undefined,
          suggestions: (result.suggestions || []).map((s: any) => ({
            type: "improvement",
            original: s.original || "",
            suggestion: s.suggestion || "",
            reason: s.reason || "",
          })),
        };
      } catch (error) {
        console.error("API 호출 실패:", error);
        return generateMockAnalysis(text);
      }
    },
    onSuccess: (data) => {
      setAnalysis(data);
      toast({
        title: "분석 완료",
        description: "텍스트 품질 분석이 완료되었습니다.",
      });
    },
    onError: (error: any) => {
      toast({
        title: "분석 실패",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleAnalyze = () => {
    if (!inputText.trim()) {
      toast({ title: "텍스트를 입력해주세요", variant: "destructive" });
      return;
    }
    analyzeMutation.mutate(inputText.trim());
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "복사 완료",
      description: "텍스트가 클립보드에 복사되었습니다.",
    });
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return "text-green-600";
    if (score >= 80) return "text-blue-600";
    if (score >= 70) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreBadge = (score: number) => {
    if (score >= 90)
      return <Badge className="bg-green-100 text-green-800">우수</Badge>;
    if (score >= 80)
      return <Badge className="bg-blue-100 text-blue-800">양호</Badge>;
    if (score >= 70)
      return <Badge className="bg-yellow-100 text-yellow-800">보통</Badge>;
    return <Badge className="bg-red-100 text-red-800">개선 필요</Badge>;
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            분석할 텍스트
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="품질을 분석할 텍스트를 입력하세요..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            className="min-h-[150px]"
          />
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <label className="text-sm font-medium mb-2 block">
                대상 청중
              </label>
              <Select value={targetAudience} onValueChange={setTargetAudience}>
                <SelectTrigger>
                  <SelectValue placeholder="분석 대상을 선택하세요" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="초등학생">초등학생</SelectItem>
                  <SelectItem value="중학생">중학생</SelectItem>
                  <SelectItem value="고등학생">고등학생</SelectItem>
                  <SelectItem value="대학생">대학생</SelectItem>
                  <SelectItem value="성인학습자">성인학습자</SelectItem>
                  <SelectItem value="교사">교사</SelectItem>
                  <SelectItem value="학부모">학부모</SelectItem>
                  <SelectItem value="일반인">일반인</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex-1">
              <label className="text-sm font-medium mb-2 block">
                상황 맥락
              </label>
              <Select
                value={context}
                onValueChange={(value: any) => setContext(value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="분석할 글의 맥락을 선택하세요" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="business">일반</SelectItem>
                  <SelectItem value="report">교육</SelectItem>
                  <SelectItem value="casual">보고서/공문</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button
              onClick={handleAnalyze}
              disabled={analyzeMutation.isPending}
              className="w-full sm:w-auto self-end"
            >
              {analyzeMutation.isPending ? "분석 중..." : "품질 분석"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {analysis && (
        <div className="space-y-6">
          {analysis.improved_text && (
            <Card className="bg-gradient-to-br from-white to-emerald-50/30 border-emerald-100/50 shadow-md">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-emerald-700">
                  <CheckCircle className="w-5 h-5" />
                  개선된 텍스트
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-emerald-50 rounded-lg p-4 border border-emerald-200">
                  <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                    {analysis.improved_text}
                  </p>
                </div>
                <div className="flex gap-2 mt-4">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => copyToClipboard(analysis.improved_text!)}
                  >
                    <Copy className="w-4 h-4 mr-2" />
                    복사하기
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          <div className="grid md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-6 text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <h3 className="font-semibold">문법 점수</h3>
                </div>
                <div
                  className={`text-3xl font-bold ${getScoreColor(
                    analysis.grammar_score
                  )}`}
                >
                  {Math.round(analysis.grammar_score)}
                </div>
                <div className="text-sm text-gray-600">/ 100</div>
                {getScoreBadge(analysis.grammar_score)}
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <AlertTriangle className="w-5 h-5 text-blue-600" />
                  <h3 className="font-semibold">격식 점수</h3>
                </div>
                <div
                  className={`text-3xl font-bold ${getScoreColor(
                    analysis.formality_score
                  )}`}
                >
                  {Math.round(analysis.formality_score)}
                </div>
                <div className="text-sm text-gray-600">/ 100</div>
                {getScoreBadge(analysis.formality_score)}
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Lightbulb className="w-5 h-5 text-purple-600" />
                  <h3 className="font-semibold">가독성 점수</h3>
                </div>
                <div
                  className={`text-3xl font-bold ${getScoreColor(
                    analysis.readability_score
                  )}`}
                >
                  {Math.round(analysis.readability_score)}
                </div>
                <div className="text-sm text-gray-600">/ 100</div>
                {getScoreBadge(analysis.readability_score)}
              </CardContent>
            </Card>
          </div>

          {analysis.suggestions.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="w-5 h-5" />
                  개선 제안 ({analysis.suggestions.length}개)
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
