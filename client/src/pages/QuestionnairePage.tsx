import { useEffect, useState } from "react";
import ProgressBar from "@/components/questionnaire/progress-bar";
import QuestionCard from "@/components/questionnaire/question-card";
import { questions } from "@/data/questions";
import type { UserProfile, UserResponses } from "@shared/schema";
import { useLocation } from "wouter";

// Constants management
const STORAGE_KEYS = {
  USER_ID: "chatToner_userId",
  QUESTIONNAIRE_INDEX: "chatToner_q_index",
  QUESTIONNAIRE_RESPONSES: "chatToner_q_responses",
  USER_PROFILE: "chatToner_profile",
};

// Stable UUID generation function
const generateUUID = () => {
  // Safely access crypto through globalThis for SSR and non-secure contexts
  if (globalThis?.crypto?.randomUUID) {
    return globalThis.crypto.randomUUID();
  }
  // fallback for non-secure contexts
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0,
      v = c == "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
};

const getUserId = () => {
  let id = localStorage.getItem(STORAGE_KEYS.USER_ID);
  if (!id) {
    id = generateUUID();
    localStorage.setItem(STORAGE_KEYS.USER_ID, id);
  }
  return id;
};

export default function QuestionnairePage() {
  const [, setLoc] = useLocation();
  const userId = getUserId();

  const [idx, setIdx] = useState<number>(0);
  const [responses, setResponses] = useState<Record<string, any>>({});

  useEffect(() => {
    localStorage.removeItem(STORAGE_KEYS.QUESTIONNAIRE_INDEX);
    localStorage.removeItem(STORAGE_KEYS.QUESTIONNAIRE_RESPONSES);
    setIdx(0);
    setResponses({});
  }, []);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.QUESTIONNAIRE_INDEX, JSON.stringify(idx));
  }, [idx]);

  useEffect(() => {
    localStorage.setItem(
      STORAGE_KEYS.QUESTIONNAIRE_RESPONSES,
      JSON.stringify(responses)
    );
  }, [responses]);

  const currentQuestion = questions[idx];
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
    // Logic for handling new company questionnaire responses (temporary)
    // Later, this should be integrated with backend API to create actual profiles.
    console.log("Submitting company questionnaire responses:", responses);

    const profileSummary = `주요 업무: ${
      responses.company_business_category?.[0] || "N/A"
    }\n소통 문화: ${responses.communication_style_overall?.[0] || "N/A"}`;

    // Temporarily save to localStorage and navigate to results page
    const tempProfile = {
      userId,
      companyProfile: responses,
      summary: profileSummary,
      completedAt: new Date(),
    };

    localStorage.setItem(
      STORAGE_KEYS.USER_PROFILE,
      JSON.stringify(tempProfile)
    );
    setLoc("/style-definition/results"); // Results page path may be changed to enterprise version later
  };

  const next = () =>
    idx < questions.length - 1 ? setIdx(idx + 1) : toResults();
  const prev = () => idx > 0 && setIdx(idx - 1);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "auto" });
  }, [idx]);

  return (
    <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <ProgressBar
        currentQuestion={idx + 1}
        totalQuestions={questions.length}
        progress={progress}
      />

      {currentQuestion && (
        <QuestionCard
          question={currentQuestion}
          selectedOptions={responses[currentQuestion.id] || []}
          customInput={responses[`${currentQuestion.id}_custom`] || ""}
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
