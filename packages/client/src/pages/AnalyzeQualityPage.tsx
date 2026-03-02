import { useState, useMemo } from "react";
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, ThumbsUp, Copy, Slack } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useThinkingMessage } from "@/hooks/useThinkingMessage";
import { AnalyzeQualityCard } from "@/components/Organisms/AnalyzeQualityCard";
import { Button } from "@/components/ui/button";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api, QualityAnalysisResponse } from "@/lib/api";
import { PATH } from "@/constants/paths";

export default function AnalyzeQualityPage() {
  const navigate = useNavigate();
  const { toast } = useToast();

  // State for all inputs
  const [target, setTarget] = useState<string | undefined>();
  const [situation, setSituation] = useState<string | undefined>();
  const [quality, setQuality] = useState("grammar"); // Default to 'grammar'
  const [inputText, setInputText] = useState("");

  // State for the analysis result from the API (v2)
  const [analysisResult, setAnalysisResult] = useState<QualityAnalysisResponse | null>(null);
  const [finalText, setFinalText] = useState<string>("");
  const [finalLiked, setFinalLiked] = useState<boolean>(false);

  // Mutation for v2 API
  const analyzeMutation = useMutation({
    mutationFn: async (text: string): Promise<QualityAnalysisResponse> => {
      console.log(`Analyzing text: ${text} for ${target} in ${situation}`);

      const result = await api.analyzeQuality({
        text,
        target: target!,
        context: situation!,
        company_id: "test-company",
      });

      return result;
    },
    onSuccess: (data) => {
      setAnalysisResult(data);
      setFinalText(""); // 새 분석 시 최종 글 초기화
      setFinalLiked(false);
      toast({
        title: "분석 완료",
        description: `분석 방법: ${data.method_used}, RAG 소스: ${data.rag_sources_count}개`,
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

  const handleAnalyzeClick = () => {
    if (isAnalyzeDisabled) return;
    analyzeMutation.mutate(inputText);
  };

  // 최종 글 보기 핸들러 (이미 분석 결과에 있는 final_text 사용)
  const handleShowFinalText = () => {
    if (analysisResult?.data?.final_text) {
      setFinalText(analysisResult.data.final_text);
      setFinalLiked(false);
      toast({ title: "최종 글 표시" });
    }
  };

  const isAnalyzeDisabled =
    !inputText.trim() || !target || !situation || analyzeMutation.isPending;

  // v2 Response에 맞게 출력 포맷팅
  const outputValue = useMemo(() => {
    if (analyzeMutation.isPending) {
      return "분석 중...";
    }
    if (!analysisResult || !analysisResult.data) {
      return "분석 결과가 여기에 표시됩니다";
    }

    const data = analysisResult.data;

    switch (quality) {
      case "grammar":
        return data.grammar.markdown_explanation || `점수: ${data.grammar.score}\n\n${data.grammar.justification}`;
      case "formality":
        return data.formality.markdown_explanation || `점수: ${data.formality.score}\n\n${data.formality.justification}`;
      case "protocol":
        return data.protocol.markdown_explanation || `점수: ${data.protocol.score}\n\n${data.protocol.justification}`;
      default:
        return "분석 항목을 선택해주세요.";
    }
  }, [analysisResult, quality, analyzeMutation.isPending, thinkingMessage]);

  return (
    <div className="w-full">
      <div className="mb-4">
        <Button
          variant="ghost"
          onClick={() => navigate(PATH.CHOICE)}
          className="flex items-center gap-2 text-lg"
        >
          <ArrowLeft className="h-5 w-5" />
          뒤로 가기
        </Button>
      </div>

      <h1 className="font-bold text-black text-3xl">품질 분석</h1>
      <p className="mt-1 mb-4 text-lg font-medium text-gray-700">
        문서 품질을 즉시 분석합니다
      </p>

      {/* RAG 상태 표시 */}
      {analysisResult && (
        <div className="mb-4 flex gap-2 text-sm text-gray-500">
          <span className={`px-2 py-1 rounded ${analysisResult.method_used === 'with_rag' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
            {analysisResult.method_used === 'with_rag' ? '✓ RAG 적용' : '⚠ RAG 미적용'}
          </span>
          <span className="px-2 py-1 rounded bg-blue-100 text-blue-700">
            신뢰도: {analysisResult.confidence_level}
          </span>
          <span className="px-2 py-1 rounded bg-gray-100">
            처리 시간: {analysisResult.processing_time?.toFixed(2)}초
          </span>
        </div>
      )}

      <div className="flex justify-center w-full px-4">
        <AnalyzeQualityCard
          targetValue={target}
          onTargetChange={setTarget}
          situationValue={situation}
          onSituationChange={setSituation}
          qualityValue={quality}
          onQualityChange={setQuality}
          inputValue={inputText}
          onInputChange={setInputText}
          outputValue={outputValue}
          isAnalyzeDisabled={isAnalyzeDisabled}
          onAnalyzeClick={handleAnalyzeClick}
        />
      </div>

      {/* 최종 글 섹션 */}
      {analysisResult && (
        <div className="mt-6 flex flex-col items-center gap-4">
          <Button
            size="sm"
            className="rounded-full ring-1 ring-primary shadow-[0_0_12px_rgba(59,130,246,0.65)] hover:shadow-[0_0_16px_rgba(59,130,246,0.85)]"
            disabled={!analysisResult?.data?.final_text}
            onClick={handleShowFinalText}
          >
            {finalText ? "최종 글 다시보기" : "최종 글 보기"}
          </Button>

          {finalText && (
            <div className="w-full max-w-4xl">
              <div className="mb-2 flex items-center justify-between">
                <h2 className="text-xl font-semibold">최종 글</h2>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      navigator.clipboard.writeText(finalText);
                      toast({ title: "클립보드에 복사되었습니다!" });
                    }}
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    복사
                  </Button>
                  <a href="https://slack.com" target="_blank" rel="noopener noreferrer">
                    <Button size="sm" variant="outline">
                      <Slack className="h-4 w-4" />
                    </Button>
                  </a>
                  <Button
                    size="sm"
                    variant={finalLiked ? "default" : "secondary"}
                    className={[
                      "gap-2 rounded-full",
                      finalLiked
                        ? "ring-2 ring-emerald-400 shadow-[0_0_14px_rgba(16,185,129,0.55)]"
                        : "ring-1 ring-primary/40 hover:shadow-[0_0_12px_rgba(59,130,246,0.45)]",
                    ].join(" ")}
                    aria-pressed={finalLiked}
                    disabled={finalLiked}
                    onClick={() => {
                      setFinalLiked(true);
                      toast({ title: "피드백 반영", description: "좋아요가 반영되었습니다." });
                    }}
                  >
                    <ThumbsUp className="h-4 w-4" /> {finalLiked ? "반영됨" : "좋아요"}
                  </Button>
                </div>
              </div>
              <div
                className={[
                  "prose max-w-none border rounded-lg p-5 bg-white transition-shadow",
                  finalLiked ? "shadow-[0_0_18px_rgba(16,185,129,0.35)]" : "",
                ].join(" ")}
              >
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{finalText}</ReactMarkdown>
              </div>

              {/* 요약 */}
              {analysisResult.data?.summary && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-medium text-gray-700 mb-2">요약</h3>
                  <p className="text-gray-600">{analysisResult.data.summary}</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
