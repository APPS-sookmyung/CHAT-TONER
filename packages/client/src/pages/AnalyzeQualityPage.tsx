import { useState, useMemo, useRef } from "react";
import { flushSync } from "react-dom";
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, ThumbsUp, Copy } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useThinkingMessage } from "@/hooks/useThinkingMessage";
import { AnalyzeQualityCard } from "@/components/Organisms/AnalyzeQualityCard";
import { Button } from "@/components/Atoms/Button";
import { Button as UiButton } from "@/components/ui/button";
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
  const resultRef = useRef<HTMLDivElement>(null);

  // Mutation for v2 API
  const analyzeMutation = useMutation({
    mutationFn: async (text: string): Promise<QualityAnalysisResponse> => {
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
      // flushSync로 DOM 업데이트를 동기적으로 완료한 뒤 스크롤
      flushSync(() => {
        setFinalText(analysisResult.data.final_text);
        setFinalLiked(false);
      });
      resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  const isAnalyzeDisabled =
    !inputText.trim() || !target || !situation || analyzeMutation.isPending;

  // v2 Response에 맞게 출력 포맷팅
  const thinkingMessage = useThinkingMessage(analyzeMutation.isPending);

  const outputValue = useMemo(() => {
    if (analyzeMutation.isPending) {
      return thinkingMessage;
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
        <UiButton
          variant="ghost"
          onClick={() => navigate(PATH.CHOICE)}
          className="flex items-center gap-2 text-lg"
        >
          <ArrowLeft className="h-5 w-5" />
          뒤로 가기
        </UiButton>
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

      {/* 분석 완료 후 최종 글 보기 — 화면 하단 고정 플로팅 버튼 */}
      {analysisResult && !finalText && (
        <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50">
          <Button
            size="xl"
            className="px-16 shadow-xl"
            disabled={!analysisResult?.data?.final_text}
            onClick={handleShowFinalText}
          >
            최종 글 보기
          </Button>
        </div>
      )}

      {/* 최종 글 결과 카드 */}
      {finalText && (
        <div ref={resultRef} className="mt-8 w-full max-w-7xl animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="bg-surface rounded-2xl p-8 flex flex-col gap-6">
                {/* 헤더 */}
                <div className="flex items-center justify-between pb-1">
                  <h2 className="text-lg font-bold text-gray-800">최종 결과물</h2>
                  <div className="flex items-center gap-2">
                    <button
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white hover:bg-gray-50 text-gray-700 text-sm font-bold border border-gray-200 transition-all active:scale-95"
                      onClick={() => {
                        navigator.clipboard.writeText(finalText);
                        toast({ title: "클립보드에 복사되었습니다!" });
                      }}
                    >
                      <Copy className="h-4 w-4" />
                      복사
                    </button>
                    <a
                      href="https://slack.com"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center justify-center w-8 h-8 rounded-xl bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 transition-all active:scale-95 no-underline"
                    >
                      <svg viewBox="0 0 122.8 122.8" className="h-4 w-4">
                        <path d="M21 70.7c0 5.8-4.7 10.6-10.5 10.6S0 76.5 0 70.7s4.7-10.6 10.5-10.6h10.5v10.6zm5.3 0c0-5.8 4.7-10.6 10.5-10.6s10.5 4.7 10.5 10.6v26.3c0 5.8-4.7 10.6-10.5 10.6s-10.5-4.7-10.5-10.6V70.7z" fill="#e01e5a"/><path d="M52.1 21c-5.8 0-10.6-4.7-10.6-10.5S46.2 0 52.1 0s10.6 4.7 10.6 10.5V21h-10.6zm0 5.3c5.8 0 10.6 4.7 10.6 10.5s-4.7 10.6-10.6 10.6H25.8c-5.8 0-10.6-4.7-10.6-10.6s4.7-10.5 10.6-10.5h26.3z" fill="#36c5f0"/><path d="M101.8 52.1c0-5.8 4.7-10.6 10.5-10.6s10.5 4.7 10.5 10.6-4.7 10.6-10.5 10.6h-10.5V52.1zm-5.3 0c0 5.8-4.7 10.6-10.5 10.6s-10.5-4.7-10.5-10.6V25.8c0-5.8 4.7-10.6 10.5-10.6s10.5 4.7 10.5 10.6v26.3z" fill="#2eb67d"/><path d="M70.7 101.8c5.8 0 10.6 4.7 10.6 10.5s-4.7 10.5-10.6 10.5-10.6-4.7-10.6-10.5V101.8h10.6zm0-5.3c-5.8 0-10.6-4.7-10.6-10.5s4.7-10.6 10.6-10.6h26.3c5.8 0 10.6 4.7 10.6 10.6s-4.7 10.5-10.6 10.5H70.7z" fill="#ecb22e"/>
                      </svg>
                    </a>
                    <button
                      className={[
                        "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-sm font-bold border border-gray-200 transition-all active:scale-95",
                        finalLiked
                          ? "bg-primary text-white border-none"
                          : "bg-white hover:bg-gray-50 text-gray-700",
                      ].join(" ")}
                      disabled={finalLiked}
                      onClick={() => {
                        setFinalLiked(true);
                        toast({ title: "피드백 반영", description: "좋아요가 반영되었습니다." });
                      }}
                    >
                      <ThumbsUp className={`h-4 w-4 ${finalLiked ? "fill-white" : ""}`} />
                      {finalLiked ? "반영됨" : "좋아요"}
                    </button>
                  </div>
                </div>

                {/* 본문 — 흰색 textarea 스타일 */}
                <div className="w-full min-h-[300px] bg-white rounded-2xl p-8 text-lg text-gray-800 prose prose-lg max-w-none border border-gray-200 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden overflow-y-auto">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{finalText}</ReactMarkdown>
                </div>

                {/* 요약 */}
                {analysisResult?.data?.summary && (
                  <div className="p-6 bg-white/50 rounded-2xl border border-gray-100/50">
                    <h3 className="font-bold text-sm text-gray-700 mb-2 flex items-center gap-2">
                      <div className="w-1.5 h-3.5 bg-primary/40 rounded-full" />
                      요약
                    </h3>
                    <p className="text-sm text-gray-600 leading-relaxed font-medium">{analysisResult?.data?.summary}</p>
                  </div>
                )}
          </div>
        </div>
      )}
    </div>
  );
}
