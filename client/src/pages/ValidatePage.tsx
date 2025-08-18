import QualityValidator from "@/components/quality-validator";
import { Button } from "@/components/ui/button";
import { useLocation } from "wouter";

export default function ValidatePage() {
  const [, setLoc] = useLocation();
  return (
    <main className="max-w-6xl mx-auto p-8">
      <div className="mb-4">
        <Button
          variant="outline"
          onClick={() => setLoc("/")}
          className="bg-white border-gray-200"
        >
          ← 모드 선택으로
        </Button>
      </div>
      <QualityValidator onBack={() => setLoc("/")} />
    </main>
  );
}
