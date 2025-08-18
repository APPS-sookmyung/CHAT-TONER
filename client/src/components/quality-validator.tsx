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
  ArrowLeft,
  BarChart3,
  CheckCircle,
  AlertTriangle,
  Lightbulb,
  Copy,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface QualityValidatorProps {
  onBack: () => void;
}

interface QualityAnalysis {
  grammar_score: number;
  formality_score: number;
  readability_score: number;
  suggestions: Array<{
    type: string;
    original: string;
    suggestion: string;
    reason: string;
    confidence: number;
  }>;
}

// 임시 모의 데이터 생성 함수
const generateMockAnalysis = (text: string): QualityAnalysis => {
  const words = text.split(' ').length;
  const sentences = text.split(/[.!?]+/).filter(s => s.trim()).length;
  
  return {
    grammar_score: Math.floor(Math.random() * 30) + 70, // 70-100
    formality_score: Math.floor(Math.random() * 40) + 60, // 60-100
    readability_score: Math.floor(Math.random() * 25) + 75, // 75-100
    suggestions: [
      {
        type: "grammar",
        original: "잘못된 문법 예시",
        suggestion: "올바른 문법 예시",
        reason: "문법적 오류를 수정하여 더 명확한 표현이 됩니다.",
        confidence: 0.85
      },
      {
        type: "style",
        original: "비격식 표현",
        suggestion: "격식 표현",
        reason: "업무 환경에 적합한 격식 있는 표현으로 변경합니다.",
        confidence: 0.78
      },
      {
        type: "clarity",
        original: "모호한 표현",
        suggestion: "명확한 표현",
        reason: "의미를 더 명확하게 전달할 수 있도록 개선합니다.",
        confidence: 0.92
      }
    ].slice(0, Math.min(3, Math.floor(words / 20) + 1)) // 텍스트 길이에 따라 제안 개수 조절
  };
};

export default function QualityValidator({ onBack }: QualityValidatorProps) {
  const [inputText, setInputText] = useState("");
  const [context, setContext] = useState<"business" | "report" | "casual">(
    "business"
  );
  const [analysis, setAnalysis] = useState<QualityAnalysis | null>(null);
  const { toast } = useToast();

  const analyzeMutation = useMutation({
    mutationFn: async (text: string): Promise<QualityAnalysis> => {
      // 백엔드 API 대신 모의 데이터 사용
      await new Promise(resolve => setTimeout(resolve, 1000)); // 1초 지연으로 실제 분석 중인 것처럼 보이게
      return generateMockAnalysis(text);
    },
    onSuccess: (data) => {
      setAnalysis(data);
      toast({
        title: "분석 완료",
        description: "텍스트 품질 분석이 완료되었습니다.",
      });
    },
    onError: (error) => {
      toast({
        title: "분석 실패",
        description:
          error instanceof Error
            ? error.message
            : "알 수 없는 오류가 발생했습니다.",
        variant: "destructive",
      });
    },
  });

  const handleAnalyze = () => {
    if (!inputText.trim()) {
      toast({
        title: "텍스트를 입력해주세요",
        description: "분석할 텍스트를 입력해주세요.",
        variant: "destructive",
      });
      return;
    }

    analyzeMutation.mutate(inputText.trim());
  };

  const applySuggestion = (original: string, suggestion: string) => {
    const newText = inputText.replace(original, suggestion);
    setInputText(newText);
    toast({
      title: "개선 적용",
      description: `"${original}" → "${suggestion}"으로 변경되었습니다.`,
    });
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
    if (score >= 90) return <Badge className="bg-green-100 text-green-800">우수</Badge>;
    if (score >= 80) return <Badge className="bg-blue-100 text-blue-800">양호</Badge>;
    if (score >= 70) return <Badge className="bg-yellow-100 text-yellow-800">보통</Badge>;
    return <Badge className="bg-red-100 text-red-800">개선 필요</Badge>;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={onBack} size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            돌아가기
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">품질 분석기</h1>
            <p className="text-gray-600">텍스트의 품질을 분석하고 개선 방안을 제시합니다</p>
          </div>
        </div>
      </div>

      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            텍스트 분석
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="분석할 텍스트를 입력하세요..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            className="min-h-[150px]"
          />

          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="text-sm font-medium mb-2 block">
                분석 맥락
              </label>
              <Select
                value={context}
                onValueChange={(value: "business" | "report" | "casual") =>
                  setContext(value)
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  <SelectItem value="business">업무/비즈니스</SelectItem>
                  <SelectItem value="report">보고서/공문</SelectItem>
                  <SelectItem value="casual">일상/캐주얼</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button
              onClick={handleAnalyze}
              disabled={analyzeMutation.isPending}
              className="min-w-[120px]"
            >
              {analyzeMutation.isPending ? "분석 중..." : "품질 분석"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysis && (
        <div className="space-y-6">
          {/* Score Cards */}
          <div className="grid md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-6 text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <h3 className="font-semibold">문법 점수</h3>
                </div>
                <div className={`text-3xl font-bold ${getScoreColor(analysis.grammar_score)}`}>
                  {analysis.grammar_score}
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
                <div className={`text-3xl font-bold ${getScoreColor(analysis.formality_score)}`}>
                  {analysis.formality_score}
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
                <div className={`text-3xl font-bold ${getScoreColor(analysis.readability_score)}`}>
                  {analysis.readability_score}
                </div>
                <div className="text-sm text-gray-600">/ 100</div>
                {getScoreBadge(analysis.readability_score)}
              </CardContent>
            </Card>
          </div>

          {/* Suggestions */}
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
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <Badge variant="outline" className="capitalize">
                          {suggestion.type}
                        </Badge>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => applySuggestion(suggestion.original, suggestion.suggestion)}
                          >
                            적용
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => copyToClipboard(suggestion.suggestion)}
                          >
                            <Copy className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div>
                          <span className="text-sm text-gray-600">원문: </span>
                          <span className="text-red-600 line-through">{suggestion.original}</span>
                        </div>
                        <div>
                          <span className="text-sm text-gray-600">제안: </span>
                          <span className="text-green-600 font-medium">{suggestion.suggestion}</span>
                        </div>
                        <div>
                          <span className="text-sm text-gray-600">이유: </span>
                          <span className="text-gray-700">{suggestion.reason}</span>
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
