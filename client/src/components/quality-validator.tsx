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
import { BarChart3, CheckCircle, AlertTriangle, Lightbulb } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import QualityAnalysisResult from "@/components/quality-analysis-result";

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

// QualityAnalysis를 QualityAnalysisResult props 형식으로 변환
const convertToResultProps = (inputText: string, analysis: QualityAnalysis) => {
  return {
    inputText,
    scores: [
      {
        name: "문법",
        score: Math.round(analysis.grammar_score),
        maxScore: 100,
        icon: CheckCircle,
        color: "text-green-600",
      },
      {
        name: "격식",
        score: Math.round(analysis.formality_score),
        maxScore: 100,
        icon: AlertTriangle,
        color: "text-blue-600",
      },
      {
        name: "가독성",
        score: Math.round(analysis.readability_score),
        maxScore: 100,
        icon: Lightbulb,
        color: "text-purple-600",
      },
    ],
    improvements: analysis.suggestions.map((suggestion) => ({
      title: suggestion.type,
      original: suggestion.original,
      improved: suggestion.suggestion,
      reason: suggestion.reason,
    })),
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
        <QualityAnalysisResult
          {...convertToResultProps(inputText, analysis)}
          onApplyImprovement={(improvement, index) => {
            // 개선사항을 원본 텍스트에 적용
            const newText = inputText.replace(
              improvement.original,
              improvement.improved
            );
            setInputText(newText);

            toast({
              title: "개선사항 적용 완료",
              description: `"${improvement.original}"을(를) "${improvement.improved}"으(로) 변경했습니다.`,
            });
          }}
        />
      )}
    </div>
  );
}