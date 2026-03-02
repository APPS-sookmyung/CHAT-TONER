import { Button } from "@/components/Atoms/Button";
import { Textarea } from "@/components/Atoms/Textarea";
import { Card } from "@/components/Molecules/Card";
import { Dropdown } from "@/components/Molecules/Dropdown";
import { SegmentedControl } from "@/components/Molecules/SegmentedControl";
import { situationOptions, targetOptions } from "@/constants/dropdownOptions";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const qualityOptions = [
  { label: "Grammar", value: "grammar" },
  { label: "Formality", value: "formality" },
  { label: "Protocol", value: "protocol" },
];

// Define the props for the controlled component
interface AnalyzeQualityCardProps {
  targetValue?: string;
  onTargetChange: (value: string) => void;
  situationValue?: string;
  onSituationChange: (value: string) => void;
  qualityValue: string;
  onQualityChange: (value: string) => void;
  inputValue: string;
  onInputChange: (value: string) => void;
  outputValue: string;
  isAnalyzeDisabled: boolean;
  onAnalyzeClick: () => void;
}

export const AnalyzeQualityCard = ({
  targetValue,
  onTargetChange,
  situationValue,
  onSituationChange,
  qualityValue,
  onQualityChange,
  inputValue,
  onInputChange,
  outputValue,
  isAnalyzeDisabled,
  onAnalyzeClick,
}: AnalyzeQualityCardProps) => {
  return (
    <div className="flex flex-col items-stretch gap-8 lg:flex-row lg:gap-[58px] w-full max-w-7xl">
      <Card variant="primary" size="large" className="flex-1 flex flex-col">
        <div className="flex flex-col justify-between h-full">
          <div className="flex flex-col gap-4 flex-1">
            <div className="flex gap-4 w-full">
              <div className="flex-[1] min-w-0">
                <Dropdown
                  options={targetOptions}
                  value={targetValue}
                  onChange={onTargetChange}
                  placeholder="Target"
                  variant="target"
                  size="full"
                />
              </div>
              <div className="flex-[2] min-w-0">
                <Dropdown
                  options={situationOptions}
                  value={situationValue}
                  onChange={onSituationChange}
                  placeholder="Situation"
                  variant="situation"
                  size="full"
                />
              </div>
            </div>
            <Textarea
              value={inputValue}
              onChange={(e) => onInputChange(e.target.value)}
              placeholder="Enter your text"
              rows={8}
              className="flex-1"
            />
          </div>

          <Button size="xl" onClick={onAnalyzeClick} disabled={isAnalyzeDisabled} className="mt-4">
            Analyze
          </Button>
        </div>
      </Card>

      <div className="flex flex-col gap-13 flex-1 items-stretch">
        <SegmentedControl
          options={qualityOptions}
          value={qualityValue}
          onChange={onQualityChange}
          className="w-full"
        />
        <Card variant="primary" size="large" className="flex-1 flex flex-col">
          <div className="flex flex-col justify-between h-full gap-4 flex-1">
            {outputValue && outputValue !== "Analyzed text will appear here" ? (
              <div className="w-full min-h-[300px] flex-1 overflow-y-auto p-6 bg-white rounded-[20px] border border-gray-200 text-sm text-text-primary prose prose-sm max-w-none text-left [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{outputValue}</ReactMarkdown>
              </div>
            ) : (
              <div className="w-full min-h-[300px] flex-1 p-6 bg-white rounded-[20px] border border-primary text-sm text-text-secondary flex items-center justify-center">
                Analyzed text will appear here
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};