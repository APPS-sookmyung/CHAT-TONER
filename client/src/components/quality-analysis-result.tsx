import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  CheckCircle,
  AlertTriangle,
  Lightbulb,
  Copy,
  Check,
} from "lucide-react";
import { useState } from "react";

interface QualityScore {
  name: string;
  score: number;
  maxScore: number;
  icon: any;
  color: string;
}

interface Improvement {
  title: string;
  original: string;
  improved: string;
  reason: string;
}

interface QualityAnalysisResultProps {
  inputText?: string;
  scores: QualityScore[];
  improvements: Improvement[];
  onApplyImprovement?: (improvement: Improvement, index: number) => void;
}

export default function QualityAnalysisResult({
  inputText,
  scores,
  improvements,
  onApplyImprovement = () => {}, // 기본값: 빈 함수
}: QualityAnalysisResultProps) {
  return (
    <div className="space-y-6">
      {/* 품질 점수 카드들 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {scores.map((score, index) => (
          <Card key={index} className="text-center">
            <CardContent className="p-6">
              <div className="flex items-center justify-center mb-4">
                <score.icon className={`w-6 h-6 ${score.color}`} />
                <span className="ml-2 font-semibold text-gray-700">
                  {score.name}
                </span>
              </div>
              <div className="mb-4">
                <span className="text-3xl font-bold text-red-500">
                  {score.score}
                </span>
                <span className="text-gray-500 ml-1">/ {score.maxScore}</span>
              </div>
              {score.score < score.maxScore * 0.7 && (
                <Button
                  variant="outline"
                  size="sm"
                  className="text-red-500 border-red-200"
                >
                  개선 필요
                </Button>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 개선 제안 리스트 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-[#00C4B7]" />
            개선 제안 ({improvements.length}개)
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {improvements.map((improvement, index) => (
            <ImprovementItem
              key={index}
              improvement={improvement}
              onApply={() => onApplyImprovement(improvement, index)}
            />
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

function ImprovementItem({
  improvement,
  onApply = () => {},
}: {
  improvement: Improvement;
  onApply?: () => void;
}) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(improvement.improved);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="border rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <span className="font-medium text-gray-900">{improvement.title}</span>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={onApply}>
            적용
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleCopy}
            className="flex items-center gap-2"
          >
            {copied ? (
              <Check className="w-4 h-4" />
            ) : (
              <Copy className="w-4 h-4" />
            )}
          </Button>
        </div>
      </div>

      <div className="space-y-2">
        <div>
          <span className="text-sm text-gray-500">원문:</span>
          <span className="ml-2 text-gray-700">{improvement.original}</span>
        </div>
        <div>
          <span className="text-sm text-gray-500">제안:</span>
          <span className="ml-2 text-[#00C4B7] font-medium">
            {improvement.improved}
          </span>
        </div>
        <div>
          <span className="text-sm text-gray-500">이유:</span>
          <span className="ml-2 text-gray-600 text-sm">
            {improvement.reason}
          </span>
        </div>
      </div>
    </div>
  );
}
