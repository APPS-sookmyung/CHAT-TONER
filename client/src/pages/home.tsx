import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { MessageSquare, Settings, ArrowRightLeft, Filter } from "lucide-react";
import ProgressBar from "@/components/questionnaire/progress-bar";
import QuestionCard from "@/components/questionnaire/question-card";
import ResultsSummary from "@/components/questionnaire/results-summary";
import ProfileSummary from "@/components/converter/profile-summary";
import NewTextConverter from "@/components/converter/new-text-converter";
import ModeSelector from "@/components/mode-selector";
import QualityValidator from "@/components/quality-validator";
import { NegativePromptSettings } from "@/components/negative-prompt-settings";
import { questions } from "@/data/questions";
import type { UserProfile, UserResponses } from "@shared/schema";
import { Link, useLocation } from "wouter";

type Phase =
  | "mode-select"
  | "questionnaire"
  | "converter"
  | "results"
  | "validate";

export default function Home() {
  const [currentPhase, setCurrentPhase] = useState<Phase>("mode-select");
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [responses, setResponses] = useState<Record<string, any>>({});
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [userId] = useState(() => `user_${Date.now()}`); // Simple user ID generation
  const [, setLocation] = useLocation();

  // Load saved state from localStorage and check for existing profile
  useEffect(() => {
    const savedState = localStorage.getItem("chatToner_state");
    if (savedState) {
      try {
        const state = JSON.parse(savedState);
        setCurrentPhase(state.currentPhase || "mode-select");
        setCurrentQuestionIndex(state.currentQuestionIndex || 0);
        setResponses(state.responses || {});
        setUserProfile(state.userProfile || null);
      } catch (error) {
        console.error("Failed to load saved state:", error);
      }
    }

    // Also check if profile exists in database
    const checkExistingProfile = async () => {
      try {
        const response = await fetch(`/api/profile/${userId}`);
        if (response.ok) {
          const existingProfile = await response.json();
          console.log("기존 프로필 발견:", existingProfile);
          setUserProfile(existingProfile);
          setCurrentPhase("converter");
        }
      } catch (error) {
        console.log("기존 프로필 없음 또는 오류:", error);
      }
    };

    checkExistingProfile();
  }, [userId]); // Removed navigate from dependencies as it doesn't change

  // Save state to localStorage
  useEffect(() => {
    const state = {
      currentPhase,
      currentQuestionIndex,
      responses,
      userProfile,
    };
    localStorage.setItem("chatToner_state", JSON.stringify(state));
  }, [currentPhase, currentQuestionIndex, responses, userProfile]);

  const handleAnswerChange = (
    questionId: string,
    selectedOptions: string[],
    customInput?: string
  ) => {
    setResponses((prev) => ({
      ...prev,
      [questionId]: selectedOptions,
      ...(customInput ? { [`${questionId}_custom`]: customInput } : {}),
    }));
  };

  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1);
    } else {
      // Complete questionnaire
      completeQuestionnaire();
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex((prev) => prev - 1);
    }
  };

  const handleSkip = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1);
    } else {
      completeQuestionnaire();
    }
  };

  const completeQuestionnaire = async () => {
    console.log("설문 완료 시작, 현재 응답:", responses);

    // Process responses into user profile format
    const processedResponses: UserResponses = {
      formality_level: parseInt(responses.formality_level?.[0] || "5"),
      friendliness_level: parseInt(responses.friendliness_level?.[0] || "5"),
      emotion_level: parseInt(responses.emotion_expression?.[0] || "5"),
      directness_level: 5, // Will be calculated from style examples later
      uses_abbreviations:
        responses.abbreviation_usage?.[0] === "자주 사용" ||
        responses.abbreviation_usage?.[0] === "매우 자주 사용",
      uses_emoticons:
        responses.emoticon_usage?.[0] === "자주 사용" ||
        responses.emoticon_usage?.[0] === "매우 자주 사용",
      gratitude_expressions: responses.gratitude_senior || [],
      request_expressions: responses.request_colleague || [],
      situation_responses: responses,
    };

    console.log("처리된 응답:", processedResponses);

    const profileData = {
      userId,
      baseFormalityLevel: processedResponses.formality_level,
      baseFriendlinessLevel: processedResponses.friendliness_level,
      baseEmotionLevel: processedResponses.emotion_level,
      baseDirectnessLevel: processedResponses.directness_level || 5,
      responses: processedResponses,
    };

    try {
      // Save profile to database
      const response = await fetch("/api/profile", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(profileData),
      });

      if (response.ok) {
        const savedProfile = await response.json();
        console.log("프로필 저장 성공:", savedProfile);
        setUserProfile(savedProfile);
        setCurrentPhase("results");
      } else {
        console.error("프로필 저장 실패:", response.status);
        // Still create local profile as fallback
        const profile: UserProfile = {
          id: 0,
          ...profileData,
          completedAt: new Date(),
        };
        setUserProfile(profile);
        setCurrentPhase("results");
      }
    } catch (error) {
      console.error("프로필 저장 중 오류:", error);
      // Still create local profile as fallback
      const profile: UserProfile = {
        id: 0,
        ...profileData,
        completedAt: new Date(),
      };
      setUserProfile(profile);
      setCurrentPhase("results");
    }
  };

  const handleStartConversion = () => {
    setCurrentPhase("converter");
  };

  const switchPhase = (phase: Phase) => {
    setCurrentPhase(phase);
  };

  const skipToConverter = async () => {
    const defaultProfileData = {
      userId,
      baseFormalityLevel: 5,
      baseFriendlinessLevel: 5,
      baseEmotionLevel: 5,
      baseDirectnessLevel: 5,
      responses: {
        formality_level: 5,
        friendliness_level: 5,
        emotion_level: 5,
        directness_level: 5,
        uses_abbreviations: false,
        uses_emoticons: false,
        gratitude_expressions: ["감사합니다"],
        request_expressions: ["도움 좀 받을 수 있을까요?"],
        situation_responses: {},
      },
    };

    try {
      // Save profile to database
      const response = await fetch("/api/profile", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(defaultProfileData),
      });

      if (response.ok) {
        const savedProfile = await response.json();
        console.log("기본 프로필 저장 성공:", savedProfile);
        setUserProfile(savedProfile);
        setCurrentPhase("converter");
      } else {
        console.error("기본 프로필 저장 실패:", response.status);
        // Still create local profile as fallback
        const defaultProfile: UserProfile = {
          id: 0,
          ...defaultProfileData,
          completedAt: new Date(),
        };
        setUserProfile(defaultProfile);
        setCurrentPhase("converter");
      }
    } catch (error) {
      console.error("기본 프로필 저장 중 오류:", error);
      // Still create local profile as fallback
      const defaultProfile: UserProfile = {
        id: 0,
        ...defaultProfileData,
        completedAt: new Date(),
      };
      setUserProfile(defaultProfile);
      setCurrentPhase("converter");
    }
  };

  const handleModeSelect = (mode: "transform" | "validate") => {
    if (mode === "transform") {
      // Check if user has profile, if not, redirect to questionnaire
      if (userProfile) {
        setCurrentPhase("converter");
      } else {
        setCurrentPhase("questionnaire");
      }
    } else {
      setCurrentPhase("validate");
    }
  };

  const handleBackToModeSelect = () => {
    setCurrentPhase("mode-select");
  };

  const getPhaseToggleText = () => {
    return currentPhase === "questionnaire" ? "변환기로 이동" : "설문으로 이동";
  };

  const currentQuestion = questions[currentQuestionIndex];
  const progress = Math.round(
    ((currentQuestionIndex + 1) / questions.length) * 100
  );
  const completionCount = Object.keys(responses).length;

  return (
    <div className="min-h-screen bg-gray-50 font-korean">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center">
                <MessageSquare className="text-white w-5 h-5" />
              </div>
              <div>
                {/* Corrected onClick handler syntax */}
                <Link href="/" className="text-xl font-bold text-gray-900">
                  Chat Toner
                </Link>
                <p className="text-sm text-gray-500">개인 맞춤형 말투 변환기</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {userProfile && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    switchPhase(
                      currentPhase === "questionnaire"
                        ? "converter"
                        : "questionnaire"
                    )
                  }
                  className="hidden md:flex items-center space-x-2"
                >
                  <ArrowRightLeft className="w-4 h-4" />
                  <span>{getPhaseToggleText()}</span>
                </Button>
              )}
              <Button variant="ghost" size="sm">
                <Settings className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentPhase === "mode-select" && (
          <ModeSelector onModeSelect={handleModeSelect} />
        )}

        {currentPhase === "validate" && (
          <QualityValidator onBack={handleBackToModeSelect} />
        )}

        {currentPhase === "questionnaire" && (
          <div className="space-y-8">
            <ProgressBar
              currentQuestion={currentQuestionIndex + 1}
              totalQuestions={questions.length}
              progress={progress}
            />

            {/* Quick Skip Option */}
            <div className="text-center">
              <Button
                variant="outline"
                onClick={skipToConverter}
                className="mb-4"
              >
                설문 건너뛰고 바로 변환기 사용하기
              </Button>
            </div>

            {currentQuestion && (
              <QuestionCard
                question={currentQuestion}
                selectedOptions={responses[currentQuestion.id] || []}
                customInput={responses[`${currentQuestion.id}_custom`] || ""}
                onAnswerChange={handleAnswerChange}
                onNext={handleNext}
                onPrevious={handlePrevious}
                onSkip={handleSkip}
                canGoBack={currentQuestionIndex > 0}
                isLastQuestion={currentQuestionIndex === questions.length - 1}
              />
            )}
          </div>
        )}

        {currentPhase === "results" && userProfile && (
          <ResultsSummary
            userProfile={userProfile}
            completionRate={100}
            onStartConversion={handleStartConversion}
            onExportData={() => {
              const dataStr = JSON.stringify(userProfile, null, 2);
              const dataBlob = new Blob([dataStr], {
                type: "application/json",
              });
              const url = URL.createObjectURL(dataBlob);
              const link = document.createElement("a");
              link.href = url;
              link.download = "chat-toner-profile.json";
              link.click();
            }}
          />
        )}

        {currentPhase === "converter" && userProfile && (
          <div className="space-y-8">
            <div className="flex items-center justify-between mb-6">
              <Button
                variant="outline"
                onClick={handleBackToModeSelect}
                className="bg-white border-gray-200"
              >
                ← 모드 선택으로 돌아가기
              </Button>

              <Tabs defaultValue="converter" className="w-full max-w-md">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger
                    value="converter"
                    className="flex items-center gap-2"
                  >
                    <ArrowRightLeft className="h-4 w-4" />
                    텍스트 변환
                  </TabsTrigger>
                  <TabsTrigger
                    value="settings"
                    className="flex items-center gap-2"
                  >
                    <Filter className="h-4 w-4" />
                    필터 설정
                  </TabsTrigger>
                </TabsList>
              </Tabs>
            </div>

            <Tabs defaultValue="converter" className="w-full">
              <TabsContent value="converter" className="space-y-8">
                <ProfileSummary userProfile={userProfile} />
                <NewTextConverter userProfile={userProfile} userId={userId} />
              </TabsContent>

              <TabsContent value="settings" className="space-y-8">
                <NegativePromptSettings
                  userId={userId}
                  onSave={(preferences) => {
                    console.log("네거티브 프롬프트 설정 저장됨:", preferences);
                  }}
                />
              </TabsContent>
            </Tabs>
          </div>
        )}
      </main>

      {/* Mobile Navigation */}
      {userProfile && (
        <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-2">
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => switchPhase("questionnaire")}
              className={`flex-1 py-3 text-center font-medium ${
                currentPhase === "questionnaire"
                  ? "text-primary border-b-2 border-primary"
                  : "text-gray-400"
              }`}
            >
              <MessageSquare className="w-5 h-5 mx-auto mb-1" />
              <span className="text-xs">설문</span>
            </button>
            <button
              onClick={() => switchPhase("converter")}
              className={`flex-1 py-3 text-center font-medium ${
                currentPhase === "converter"
                  ? "text-primary border-b-2 border-primary"
                  : "text-gray-400"
              }`}
            >
              <ArrowRightLeft className="w-5 h-5 mx-auto mb-1" />
              <span className="text-xs">변환</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
