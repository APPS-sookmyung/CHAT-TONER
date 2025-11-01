import { useState, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { questions as rawQuestions } from "@/data/questions";
import {
  SurveyStep,
  Question as SurveyStepQuestion,
} from "@/components/Organisms/SurveyStep";
import type { UserProfile } from "@shared/schema";
import { getOrSetUserId } from "@/lib/userId";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";

type SurveyResponses = Record<string, string>;

export default function SurveyPage() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { step } = useParams<{ step: string }>();
  const currentStep = parseInt(step || "1", 10);
  const [responses, setResponses] = useState<SurveyResponses>({});

  const totalSteps = rawQuestions.length;
  const rawQuestion = rawQuestions[currentStep - 1];

  const questionForStep: SurveyStepQuestion | null = useMemo(() => {
    if (!rawQuestion) return null;
    const questionType = rawQuestion.options.length > 0 ? "choice" : "text";
    return {
      number: currentStep,
      title: rawQuestion.question,
      description: rawQuestion.description,
      type: questionType,
      options:
        questionType === "choice"
          ? rawQuestion.options.map((opt) => ({ label: opt, value: opt }))
          : undefined,
      placeholder: "Type your answer here...",
      choiceSize: "sm",
    };
  }, [rawQuestion, currentStep]);

  const profileMutation = useMutation({
    mutationFn: async (answers: SurveyResponses): Promise<UserProfile> => {
      const userId = getOrSetUserId();
      const tenantId = "default-tenant"; // Using a fixed tenant ID as discussed

      try {
        // Use the new API client
        const result = await api.submitSurvey({
          tenant_id: tenantId,
          user_id: userId,
          answers: answers,
        });
        
        return result;
      } catch (error) {
        console.error("Survey submission failed:", error);
        throw new Error("Failed to submit survey. Please try again.");
      }
    },
    onSuccess: (data) => {
      // Add company_name from responses to the UserProfile data
      const finalProfileData: UserProfile = {
        ...data,
        company_name: responses["company_name"] || "N/A", // Assuming 'company_name' is the ID for the company name question
      };
      localStorage.setItem(
        "chatToner_profile",
        JSON.stringify(finalProfileData)
      );
      toast({
        title: "Success",
        description: "Your profile has been created.",
      });
      navigate("/results");
    },
    onError: (error: Error) => {
      console.error("Survey submission failed:", error);
      toast({
        title: "Submission Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleAnswerChange = (answer: string) => {
    setResponses((prev) => ({ ...prev, [rawQuestion.id]: answer }));
  };

  const handleNext = () => {
    if (currentStep < totalSteps) {
      navigate(`/survey/${currentStep + 1}`);
    } else {
      profileMutation.mutate(responses);
    }
  };

  const handlePrev = () => {
    if (currentStep > 1) {
      navigate(`/survey/${currentStep - 1}`);
    }
  };

  const currentAnswer = rawQuestion ? (responses[rawQuestion.id] ?? "") : "";

  const isNextDisabled = useMemo(() => {
    if (!questionForStep) return true;
    if (questionForStep.type === "text") return !currentAnswer.trim();
    if (questionForStep.type === "choice") return !currentAnswer;
    return false;
  }, [currentAnswer, questionForStep]);

  if (!questionForStep) {
    return <div>Question not found for this step.</div>;
  }

  return (
    <div className="flex justify-center py-8">
      <SurveyStep
        question={questionForStep}
        totalSteps={totalSteps}
        answer={currentAnswer}
        onAnswerChange={handleAnswerChange}
        onNext={handleNext}
        onPrev={handlePrev}
        isNextDisabled={isNextDisabled} // Pass the new prop
      />
    </div>
  );
}
