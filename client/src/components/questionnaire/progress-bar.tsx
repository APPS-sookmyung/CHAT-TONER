import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

interface ProgressBarProps {
  currentQuestion: number;
  totalQuestions: number;
  progress: number;
}

export default function ProgressBar({ currentQuestion, totalQuestions, progress }: ProgressBarProps) {
  return (
    <Card className="bg-white border-gray-200">
      <CardContent className="pt-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Tone Profile Collection</h2>
            <p className="text-sm text-gray-600">We analyze your unique tone of voice</p>
          </div>
          <div className="text-right">
            <span className="text-2xl font-bold text-blue-600">{currentQuestion}</span>
            <span className="text-gray-400">/</span>
            <span className="text-lg text-gray-600">{totalQuestions}</span>
          </div>
        </div>
        
        <div className="space-y-2">
          <Progress value={progress} size="lg" variant="primary" />
          <div className="flex justify-between text-sm text-gray-500">
            <span>Start</span>
            <span>Complete</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
