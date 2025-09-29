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
import { BarChart3 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import QualityAnalysisResult from "@/components/quality-analysis-result";
import type {
  CompanyQualityAnalysisResponse,
  TargetAudience,
  ContextType,
} from "@shared/schema";

const dropdownOptions = {
  target_audiences: [
    { value: "직속상사", label: "직속상사" },
    { value: "팀동료", label: "팀동료" },
    { value: "타부서담당자", label: "타부서 담당자" },
    { value: "클라이언트", label: "클라이언트" },
    { value: "외부협력업체", label: "외부 협력업체" },
    { value: "후배신입", label: "후배/신입" },
  ],
  contexts: [
    { value: "보고서", label: "보고서" },
    { value: "회의록", label: "회의록" },
    { value: "이메일", label: "이메일" },
    { value: "공지사항", label: "공지사항" },
    { value: "메시지", label: "메시지" },
  ],
};

const generateMockAnalysis = (text: string): CompanyQualityAnalysisResponse => {
  return {
    grammarScore: Math.random() * 10 + 85,
    formalityScore: Math.random() * 10 + 88,
    readabilityScore: Math.random() * 10 + 82,
    protocolScore: Math.random() * 10 + 87,
    complianceScore: Math.random() * 10 + 86,
    grammarSection: {
      score: 85,
      suggestions: [
        {
          id: "g1",
          category: "문법",
          original: "이부분",
          suggestion: "이 부분",
          reason: "Spacing error",
          severity: "low",
        },
      ],
    },
    protocolSection: {
      score: 87,
      suggestions: [
        {
          id: "p1",
          category: "프로토콜",
          original: "수고하세요",
          suggestion: "감사합니다",
          reason: "Avoid '수고하세요' according to guidelines",
          severity: "medium",
        },
      ],
    },
    companyAnalysis: {
      companyId: "test-company",
      communicationStyle: "Brief and clear",
      complianceLevel: 86,
      methodUsed: "RAG + Fine-tuning (mock)",
      processingTime: 0.5,
      ragSourcesCount: 1,
    },
  };
};

interface QualityValidatorProps {
  companyId: string;
}

export default function QualityValidator({ companyId }: QualityValidatorProps) {
  const [inputText, setInputText] = useState("");
  const [targetAudience, setTargetAudience] =
    useState<TargetAudience>("직속상사");
  const [context, setContext] = useState<ContextType>("보고서");
  const [analysis, setAnalysis] =
    useState<CompanyQualityAnalysisResponse | null>(null);
  const { toast } = useToast();

  const analyzeMutation = useMutation({
    mutationFn: async (
      text: string
    ): Promise<CompanyQualityAnalysisResponse> => {
      const userId = localStorage.getItem("chatToner_userId");
      if (!userId || !companyId) {
        const missing = [!userId && "User ID", !companyId && "Company ID"]
          .filter(Boolean)
          .join(", ");
        toast({
          title: "오류",
          description: `Cannot find ${missing}`,
          variant: "destructive",
        });
        throw new Error(`${missing} not found`);
      }

      try {
        const response = await fetch("/api/v1/quality/company/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text,
            target_audience: targetAudience,
            context: context,
            company_id: companyId,
            user_id: userId,
          }),
        });

        if (!response.ok) {
          throw new Error(`API call failed: ${response.status}`);
        }
        return response.json();
      } catch (error) {
        console.error("API call failed:", error);
        toast({
          title: "API Call Failed",
          description: "Showing mock data instead.",
          variant: "destructive",
        });
        return generateMockAnalysis(text);
      }
    },
    onSuccess: (data) => {
      setAnalysis(data);
      toast({
        title: "Analysis Complete",
        description: "Text quality analysis has been completed.",
      });
    },
    onError: (error: any) => {
      if (error.message.includes("not found")) return; // ID not found errors are already handled by toast
      toast({
        title: "Analysis Failed",
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

  const userId = localStorage.getItem("chatToner_userId");

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            기업용 품질 분석
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="품질을 분석할 텍스트를 입력하세요..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            className="min-h-[150px]"
          />
          <div className="flex flex-col gap-4 sm:flex-row">
            <div className="flex-1">
              <label className="block mb-2 text-sm font-medium">대상</label>
              <Select
                value={targetAudience}
                onValueChange={(v) => setTargetAudience(v as TargetAudience)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="대상을 선택하세요" />
                </SelectTrigger>
                <SelectContent>
                  {dropdownOptions.target_audiences.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex-1">
              <label className="block mb-2 text-sm font-medium">상황</label>
              <Select
                value={context}
                onValueChange={(v) => setContext(v as ContextType)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="상황을 선택하세요" />
                </SelectTrigger>
                <SelectContent>
                  {dropdownOptions.contexts.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button
              onClick={handleAnalyze}
              disabled={analyzeMutation.isPending}
              className="self-end w-full sm:w-auto"
            >
              {analyzeMutation.isPending ? "분석 중..." : "품질 분석"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {analysis && userId && companyId && (
        <QualityAnalysisResult
          analysisResult={analysis}
          originalText={inputText}
          targetAudience={targetAudience}
          context={context}
          userId={userId}
          companyId={companyId}
          onApplySuggestion={(original, suggestion) => {
            setInputText((prev) => prev.replace(original, suggestion));
            toast({
              title: "적용 완료",
              description: "제안이 텍스트에 반영되었습니다.",
            });
          }}
        />
      )}
    </div>
  );
}