import QualityValidator from "@/components/quality-validator";
import { Button } from "@/components/ui/button";
import { useLocation } from "wouter";

export default function ValidatePage() {
  const [, setLocation] = useLocation();

  const handleGoHome = () => {
    setLocation("/");
  };

  // Later, the actual company ID should be obtained from parent context or state management library.
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
