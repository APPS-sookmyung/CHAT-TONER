import { useEffect, useState } from "react";
import ProgressBar from "@/components/questionnaire/progress-bar";
import QuestionCard from "@/components/questionnaire/question-card";
import { questions } from "@/data/questions";
import type { UserProfile, UserResponses } from "@shared/schema";
import { useLocation } from "wouter";

const USER_ID_KEY = "chatToner_userId";
const getUserId = () => {
  let id = localStorage.getItem(USER_ID_KEY);
  if (!id) {
    id = crypto?.randomUUID?.() ?? `user_${Date.now()}`;
    localStorage.setItem(USER_ID_KEY, id);
  }
  return id;
};

export default function QuestionnairePage() {
  const [, setLoc] = useLocation();
  const userId = getUserId();

  const [idx, setIdx] = useState<number>(0); // 항상 첫 번째 페이지부터 시작
  const [responses, setResponses] = useState<Record<string, any>>({});

  // 설문조사 페이지 진입 시 항상 초기화
  useEffect(() => {
    localStorage.removeItem("chatToner_q_index");
    localStorage.removeItem("chatToner_q_responses");
    setIdx(0);
    setResponses({});
  }, []);

  useEffect(() => {
    localStorage.setItem("chatToner_q_index", JSON.stringify(idx));
  }, [idx]);
  useEffect(() => {
    localStorage.setItem("chatToner_q_responses", JSON.stringify(responses));
  }, [responses]);

  const current = questions[idx];
  const progress = Math.round(((idx + 1) / questions.length) * 100);

  const handleAnswerChange = (
    qid: string,
    selected: string[],
    custom?: string
  ) => {
    setResponses((prev) => ({
      ...prev,
      [qid]: selected,
      ...(custom ? { [`${qid}_custom`]: custom } : {}),
    }));
  };

  const toResults = async () => {
    const processed: UserResponses = {
      formality_level: parseInt(responses.formality_level?.[0] || "5"),
      friendliness_level: parseInt(responses.friendliness_level?.[0] || "5"),
      emotion_level: parseInt(responses.emotion_expression?.[0] || "5"),
      directness_level: 5,
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

    const profileData = {
      userId,
      baseFormalityLevel: processed.formality_level,
      baseFriendlinessLevel: processed.friendliness_level,
      baseEmotionLevel: processed.emotion_level,
      baseDirectnessLevel: processed.directness_level || 5,
      responses: processed,
    };

    // 백엔드 API 없이 로컬 스토리지만 사용
    const saved: UserProfile = {
      id: 0,
      ...profileData,
      completedAt: new Date(),
    } as UserProfile;

    localStorage.setItem("chatToner_profile", JSON.stringify(saved));
    setLoc("/style-definition/results");
  };

  const next = () =>
    idx < questions.length - 1 ? setIdx(idx + 1) : toResults();
  const prev = () => idx > 0 && setIdx(idx - 1);

  const skipAllToConverter = async () => {
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

    // 백엔드 API 없이 로컬 스토리지만 사용
    const saved: UserProfile = {
      id: 0,
      ...defaultProfileData,
      completedAt: new Date(),
    } as UserProfile;

    localStorage.setItem("chatToner_profile", JSON.stringify(saved));
    setLoc("/converter");
  };

  useEffect(() => window.scrollTo({ top: 0, behavior: "auto" }), [idx]);

  return (
    <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <ProgressBar
        currentQuestion={idx + 1}
        totalQuestions={questions.length}
        progress={progress}
      />

      {current && (
        <QuestionCard
          question={current}
          selectedOptions={responses[current.id] || []}
          customInput={responses[`${current.id}_custom`] || ""}
          onAnswerChange={handleAnswerChange}
          onNext={next}
          onPrevious={prev}
          canGoBack={idx > 0}
          isLastQuestion={idx === questions.length - 1}
        />
      )}
    </main>
  );
}
