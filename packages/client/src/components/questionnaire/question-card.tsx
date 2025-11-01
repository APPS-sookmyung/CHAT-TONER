import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Badge } from "@/components/ui/badge";
import { ChevronLeft, ChevronRight, Plus, Info } from "lucide-react";
import type { Question } from "@/data/questions";

interface QuestionCardProps {
  question: Question;
  selectedOptions: string[];
  customInput: string;
  onAnswerChange: (
    questionId: string,
    selectedOptions: string[],
    customInput?: string
  ) => void;
  onNext: () => void;
  onPrevious: () => void;
  canGoBack: boolean;
  isLastQuestion: boolean;
}

export default function QuestionCard({
  question,
  selectedOptions,
  customInput,
  onAnswerChange,
  onNext,
  onPrevious,
  canGoBack,
  isLastQuestion,
}: QuestionCardProps) {
  const [localCustomInput, setLocalCustomInput] = useState(customInput);

  const handleOptionChange = (optionValue: string, checked: boolean) => {
    let newSelected: string[];

    if (question.allowMultiple) {
      if (checked) {
        newSelected = [...selectedOptions, optionValue];
      } else {
        newSelected = selectedOptions.filter((opt) => opt !== optionValue);
      }
    } else {
      newSelected = checked ? [optionValue] : [];
    }

    onAnswerChange(question.id, newSelected, localCustomInput);
  };

  const handleCustomInputChange = (value: string) => {
    setLocalCustomInput(value);
    onAnswerChange(question.id, selectedOptions, value);
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "situational":
        return "bg-primary/10 text-primary";
      case "preferences":
        return "bg-secondary/10 text-secondary";
      case "expressions":
        return "bg-accent/10 text-accent";
      default:
        return "bg-gray-100 text-gray-600";
    }
  };

  const hasAnswer = selectedOptions.length > 0 || localCustomInput.trim();

  return (
    <Card className="border border-gray-200 shadow-sm">
      <CardContent className="p-8">
        <div className="mb-6">
          <div className="flex items-center mb-3 space-x-2">
            <Badge
              className={`${getCategoryColor(question.category)} font-medium`}
            >
              {question.categoryLabel}
            </Badge>
            {question.allowMultiple && (
              <div className="flex items-center space-x-1 text-gray-400">
                <Info className="w-4 h-4" />
                <span className="text-xs">Multiple selections possible</span>
              </div>
            )}
          </div>
          <h3 className="mb-2 text-xl font-semibold text-gray-900">
            {question.question}
          </h3>
          <p className="text-gray-600">{question.description}</p>
        </div>

        {/* Answer Options */}
        <div className="mb-6 space-y-3">
          {question.allowMultiple ? (
            // Multiple selection
            <div className="space-y-3">
              {question.options.map((option, index) => (
                <div key={index} className="group">
                  <label
                    className={`flex items-center p-4 border-2 rounded-xl cursor-pointer transition-all duration-200 ${
                      selectedOptions.includes(option)
                        ? "border-primary bg-primary/5"
                        : "border-gray-200 hover:border-primary/30 hover:bg-primary/5"
                    }`}
                  >
                    <Checkbox
                      checked={selectedOptions.includes(option)}
                      onCheckedChange={(checked) =>
                        handleOptionChange(option, checked as boolean)
                      }
                      className="mr-4"
                    />
                    <span className="flex-1 font-medium text-gray-700">
                      {option}
                    </span>
                    {selectedOptions.includes(option) && (
                      <div className="text-primary">
                        <ChevronRight className="w-4 h-4" />
                      </div>
                    )}
                  </label>
                </div>
              ))}
            </div>
          ) : (
            // Single selection
            <RadioGroup
              value={selectedOptions[0] || ""}
              onValueChange={(value) => handleOptionChange(value, true)}
              className="space-y-3"
            >
              {question.options.map((option, index) => (
                <div key={index} className="group">
                  <label
                    className={`flex items-center p-4 border-2 rounded-xl cursor-pointer transition-all duration-200 ${
                      selectedOptions.includes(option)
                        ? "border-primary bg-primary/5"
                        : "border-gray-200 hover:border-primary/30 hover:bg-primary/5"
                    }`}
                  >
                    <RadioGroupItem value={option} className="mr-4" />
                    <span className="flex-1 font-medium text-gray-700">
                      {option}
                    </span>
                    {selectedOptions.includes(option) && (
                      <div className="text-primary">
                        <ChevronRight className="w-4 h-4" />
                      </div>
                    )}
                  </label>
                </div>
              ))}
            </RadioGroup>
          )}
        </div>

        {/* Direct input */}
        {question.allowCustom && (
          <div className="p-4 mb-6 bg-gray-50 rounded-xl">
            <div className="flex items-center mb-2 space-x-2">
              <Plus className="w-4 h-4 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">
                Direct Input
              </span>
            </div>
            <Input
              value={localCustomInput}
              onChange={(e) => handleCustomInputChange(e.target.value)}
              placeholder="Are there any other expressions you use often?"
              className="border-gray-200 focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
        )}

        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            onClick={onPrevious}
            disabled={!canGoBack}
            className="flex items-center space-x-2"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>Previous</span>
          </Button>

          <Button
            onClick={() => {
              console.log("Button clicked:", isLastQuestion ? "Complete" : "Next");
              onNext();
            }}
            disabled={false}
            className="flex items-center px-8 space-x-2"
          >
            <span>{isLastQuestion ? "Complete" : "Next"}</span>
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
