import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useLocation } from "wouter";
import { PencilRuler, Sparkles } from "lucide-react";
import { useState, useEffect } from "react";
import WelcomeModal from "@/components/welcome-modal";

export default function HomePage() {
  const [, setLocation] = useLocation();
  const [hasProfile, setHasProfile] = useState<boolean | null>(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    // 로컬 스토리지에서 프로필 확인
    let profileExists = false;
    try {
      const profile = localStorage.getItem("chatToner_profile");
      profileExists = Boolean(profile);
    } catch (error) {
      console.error("Error reading localStorage:", error);
      // localStorage 접근에 실패해도 모달은 보여줘야 하므로,
      // profileExists는 false로 유지합니다.
    }

    setHasProfile(profileExists);
    setShowModal(true); // 프로필 확인 후 즉시 모달 표시
  }, []);

  const handleStartQuestionnaire = () => {
    setShowModal(false);
    setLocation("/style-definition");
  };

  const handleCloseModal = () => {
    setShowModal(false);
  };

  const handleStyleDefinitionClick = () => {
    try {
      const profile = localStorage.getItem("chatToner_profile");
      // If profile exists, go to converter. Otherwise, go to questionnaire.
      const targetUrl = profile ? "/style-conversion" : "/style-definition";
      setLocation(targetUrl);
    } catch (error) {
      console.error("Error reading localStorage:", error);
      // Fallback to questionnaire if localStorage fails
      setLocation("/style-definition");
    }
  };

  return (
    <div className="space-y-12">
      {hasProfile !== null && (
        <WelcomeModal
          open={showModal}
          onClose={handleCloseModal}
          hasProfile={hasProfile}
          onStartQuestionnaire={handleStartQuestionnaire}
        />
      )}
      {/* 히어로 섹션 */}
      <div className="text-center py-16">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl md:text-6xl mb-6">
          언제, 어디서나 톤 맞춤 <br />
          <span className="text-[#00C4B7]">Chat Toner</span>
        </h1>
        <p className="text-lg text-gray-600 sm:text-xl md:text-2xl max-w-3xl mx-auto leading-relaxed">
          나만의 말투를 정의하고 <br />
          메시지 품질을 향상시키는 AI 도구
        </p>
      </div>

      {/* 모드 선택 섹션 */}
      <div className="max-w-5xl mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <Card className="hover:shadow-lg transition-shadow p-2">
            <CardHeader>
              <div className="flex items-center gap-4">
                <PencilRuler className="w-10 h-10 text-[#00C4B7]" />
                <div>
                  <CardTitle className="text-2xl font-bold">
                    스타일 정의
                  </CardTitle>
                  <CardDescription>
                    설문을 통해 나만의 고유한 말투를 정의합니다
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="mb-6 text-gray-600 text-lg">
                몇 가지 질문에 답하여 개인화된 텍스트 스타일 프로필을
                생성하세요. AI가 당신의 격식성, 친근함 등의 선호도를 학습합니다.
              </p>
              <Button
                onClick={handleStyleDefinitionClick}
                className="w-full text-lg py-3"
              >
                스타일 정의 시작하기
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow p-2">
            <CardHeader>
              <div className="flex items-center gap-4">
                <Sparkles className="w-10 h-10 text-[#00C4B7]" />
                <div>
                  <CardTitle className="text-2xl font-bold">
                    품질 변환
                  </CardTitle>
                  <CardDescription>
                    한국어 텍스트의 품질과 톤을 즉시 개선합니다
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="mb-6 text-gray-600 text-lg">
                텍스트를 붙여넣으면 AI가 명확성을 높이고, 오타를 수정하며, 기본
                프로필에 따라 톤을 조정합니다.
              </p>
              <Button
                onClick={() => setLocation("/quality-analysis")}
                className="w-full text-lg py-3"
              >
                분석기로 이동
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
