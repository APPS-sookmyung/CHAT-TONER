import { ReactNode, useMemo } from "react";
import { useLocation } from "wouter";
import Header from "@/components/ui/header";

/**
 * 공통 레이아웃:
 * - 상단 헤더 고정
 * - 페이지별로 헤더 토글 버튼 노출/텍스트를 경로 기반으로 제어
 */
export default function Layout({ children }: { children: ReactNode }) {
  const [path, setLocation] = useLocation();

  // 프로필 유무(있을 때만 설문/변환 토글 노출)
  const hasProfile = useMemo(() => {
    try {
      return Boolean(localStorage.getItem("chatToner_profile"));
    } catch {
      return false;
    }
  }, []);

  const isQuestionnaire = path === "/questionnaire";
  const isConverter = path === "/converter";

  const showPhaseToggle = isQuestionnaire || isConverter;
  const phaseToggleText = isQuestionnaire ? "변환기로 이동" : "설문으로 이동";

  const handlePhaseToggle = () => {
    setLocation(isQuestionnaire ? "/converter" : "/questionnaire");
  };

  return (
    <div className="min-h-screen bg-gray-50 font-korean">
      <Header
        showPhaseToggle={showPhaseToggle}
        phaseToggleText={phaseToggleText}
        onPhaseToggle={handlePhaseToggle}
      />
      {/* 공통 컨테이너 */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}
