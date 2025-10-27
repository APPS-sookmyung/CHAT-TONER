import { Button } from "@/components/Atoms/Button";
import { Textarea } from "@/components/Atoms/Textarea";
import { Card } from "@/components/Molecules/Card";
import { Dropdown } from "@/components/Molecules/Dropdown";
import { SegmentedControl } from "@/components/Molecules/SegmentedControl";
import { situationOptions, targetOptions } from "@/constants/dropdownOptions";

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
    <div className="flex flex-col items-center justify-center gap-8 lg:flex-row lg:gap-[58px]">
      <Card variant="primary" size="large">
        <div className="flex flex-col justify-between h-full">
          <div className="flex flex-col gap-4">
            <div className="flex gap-4">
              <Dropdown
                options={targetOptions}
                value={targetValue}
                onChange={onTargetChange}
                placeholder="Target"
                variant="target"
                size="compact"
              />
              <Dropdown
                options={situationOptions}
                value={situationValue}
                onChange={onSituationChange}
                placeholder="Situation"
                variant="situation"
                size="default"
              />
            </div>
            <Textarea
              value={inputValue}
              onChange={(e) => onInputChange(e.target.value)}
              placeholder="Enter your text"
            />
          </div>

          <Button size="xl" onClick={onAnalyzeClick} disabled={isAnalyzeDisabled}>
            Analyze
          </Button>
        </div>
      </Card>

      <div className="flex flex-col gap-13">
        <SegmentedControl
          options={qualityOptions}
          value={qualityValue}
          onChange={onQualityChange}
        />
        <Card variant="primary" size="medium">
          <div className="flex items-center justify-center h-full">
            <Textarea
              value={outputValue}
              placeholder="Analyzed text will appear here"
              readOnly
              rows={8}
            />
          </div>
        </Card>
      </div>
    </div>
  );
};