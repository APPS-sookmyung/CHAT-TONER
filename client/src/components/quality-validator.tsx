import React, { useState } from "react";
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

// 드롭다운 옵션을 상수로 정의
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

// Mock-up 데이터 생성 함수 (API 실패 시 사용)
const generateMockAnalysis = (text: string): CompanyQualityAnalysisResponse => {
  // ... (이하 생략, 기존 코드와 동일)
  return {
    grammarScore: Math.random() * 10 + 85,
    formalityScore: Math.random() * 10 + 88,
    readabilityScore: Math.random() * 10 + 82,
    protocolScore: Math.random() * 10 + 87,
    complianceScore: Math.random() * 10 + 86,
    grammarSection: {
      score: Math.random() * 10 + 85,
      suggestions: [
        {
          id: "g1",
          category: "문법",
          original: "이부분",
          suggestion: "이 부분",
          reason: "띄어쓰기 오류",
          severity: "low",
        },
      ],
    },
    protocolSection: {
      score: Math.random() * 10 + 87,
      suggestions: [
        {
          id: "p1",
          category: "프로토콜",
          original: "수고하세요",
          suggestion: "감사합니다",
          reason: "가이드라인에 따라 '수고하세요'는 지양",
          severity: "medium",
        },
      ],
    },
    companyAnalysis: {
      companyId: "test-company",
      communicationStyle: "간결하고 명확함",
      complianceLevel: Math.random() * 10 + 86,
      methodUsed: "RAG + Fine-tuning (mock)",
      processingTime: 0.5,
      ragSourcesCount: 1,
    },
  };
};

export default function QualityValidator() {
  const [inputText, setInputText] = useState("");
  const [targetAudience, setTargetAudience] =
    useState<TargetAudience>("직속상사");
  const [context, setContext] = useState<ContextType>("보고서");
  const [analysis, setAnalysis] =
    useState<CompanyQualityAnalysisResponse | null>(null);
  const { toast } = useToast();

  const companyId = "test-company-id"; // 임시 ID
  const userId = localStorage.getItem("chatToner_userId");

  const analyzeMutation = useMutation({
    mutationFn: async (
      text: string
    ): Promise<CompanyQualityAnalysisResponse> => {
      if (!userId) {
        toast({
          title: "오류",
          description: "사용자 ID를 찾을 수 없습니다. 다시 로그인해주세요.",
          variant: "destructive",
        });
        throw new Error("User ID not found");
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
          throw new Error(`API 호출 실패: ${response.status}`);
        }
        return response.json();
      } catch (error) {
        console.error("API 호출 실패:", error);
        toast({
          title: "API 호출 실패",
          description: "Mock 데이터를 대신 표시합니다.",
          variant: "destructive",
        });
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

      {analysis && userId && (
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
