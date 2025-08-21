import { Progress } from "@/components/ui/progress";
import { useState, useEffect } from "react";

export default function TestPage() {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 10;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-8 space-y-8">
      <h1 className="text-2xl font-bold">Progress 컴포넌트 테스트</h1>
      
      <div className="space-y-4">
        <div>
          <p className="mb-2">현재 진행률: {progress}%</p>
          <Progress value={progress} className="w-full" />
        </div>
        
        <div>
          <p className="mb-2">고정값 테스트 (50%)</p>
          <Progress value={50} className="w-full" />
        </div>
        
        <div>
          <p className="mb-2">고정값 테스트 (75%)</p>
          <Progress value={75} className="w-full" />
        </div>
        
        <div>
          <p className="mb-2">고정값 테스트 (100%)</p>
          <Progress value={100} className="w-full" />
        </div>

        <div>
          <p className="mb-2">다양한 variant 테스트</p>
          <div className="space-y-2">
            <Progress value={60} variant="default" />
            <Progress value={70} variant="primary" />
            <Progress value={80} variant="secondary" />
            <Progress value={90} variant="accent" />
          </div>
        </div>

        <div>
          <p className="mb-2">다양한 size 테스트</p>
          <div className="space-y-2">
            <Progress value={50} size="sm" />
            <Progress value={60} size="md" />
            <Progress value={70} size="lg" />
          </div>
        </div>
      </div>
    </div>
  );
}