import { Card } from "@/components/Molecules/Card";
import { ProgressBar } from "@/components/Atoms/ProgressBar";
import { Input } from "@/components/Atoms/Input";
import { ChoiceGroup } from "@/components/Molecules/ChoiceGroup";
import { Button } from "@/components/Atoms/Button";
import { useToast } from "@/hooks/use-toast";

export interface Question {
  number: number;
  title: string;
  description?: string;
  type: "text" | "choice";
  options?: { label: string; value: string }[];
  placeholder?: string;
  choiceSize?: "sm" | "lg";
}

interface SurveyStepProps {
  question: Question;
  totalSteps: number;
  answer: string;
  onAnswerChange: (answer: string) => void;
  onNext: () => void;
  onPrev: () => void;
  isNextDisabled: boolean;
}

export const SurveyStep = ({
  question,
  totalSteps,
  answer,
  onAnswerChange,
  onNext,
  onPrev,
  isNextDisabled,
}: SurveyStepProps) => {
  const { toast } = useToast();

  return (
    <div className="w-[880px] space-y-[39px]">
      <Card variant="secondary" size="small">
        <div className="flex items-center h-full">
          <ProgressBar
            label="Tone Profile Setup"
            currentStep={question.number}
            totalSteps={totalSteps}
          />
        </div>
      </Card>

      <Card variant="secondary" size="medium">
        <div className="py-8 h-full grid grid-rows-[auto_minmax(0,1fr)_auto] gap-6">
          <div className="row-start-1">
            <h2 className="text-4xl not-italic font-medium">
              {question.number}. {question.title}
            </h2>
            {question.description && (
              <p className="mt-[19px] text-2xl font-normal text-text-tertiary">
                {question.description}
              </p>
            )}
          </div>

          <div className="flex items-center justify-center row-start-2">
            <div className="w-full">
              {question.type === "text" && (
                <Input
                  value={answer}
                  onChange={(e) => onAnswerChange(e.target.value)}
                  placeholder={question.placeholder}
                />
              )}

              {question.type === "choice" && question.options && (
                <ChoiceGroup
                  options={question.options}
                  value={answer}
                  onChange={onAnswerChange}
                  size={question.choiceSize}
                />
              )}
            </div>
          </div>

          <div className="flex justify-end row-start-3 gap-2">
            <Button variant="secondary" size="sm" onClick={onPrev}>
              Previous
            </Button>

            <Button
              variant="primary"
              size="sm"
              onClick={() => {
                if (isNextDisabled) {
                  toast({
                    title: "Please provide an answer before proceeding.",
                    variant: "destructive",
                  });
                } else {
                  onNext();
                }
              }}
              disabled={isNextDisabled}
            >
              Next
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};
