import QualityValidator from "@/components/quality-validator";
import { Button } from "@/components/ui/button";
import { useLocation } from "wouter";

export default function ValidatePage() {
  const [, setLocation] = useLocation();

  const handleGoHome = () => {
    setLocation("/");
  };

  // 추후 실제 회사 ID는 상위 컨텍스트나 상태 관리 라이브러리에서 가져와야 합니다.
  const companyId = "test-company-id";

  return (
    <main className="max-w-6xl mx-auto p-8">
      <div className="mb-4">
        <Button
          variant="outline"
          onClick={handleGoHome}
          className="bg-white border-gray-200"
        >
          ← 모드 선택으로
        </Button>
      </div>
      <QualityValidator companyId={companyId} />
    </main>
  );
}
