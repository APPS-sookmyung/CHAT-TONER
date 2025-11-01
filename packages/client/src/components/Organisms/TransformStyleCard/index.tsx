import { Button } from "@/components/Atoms/Button";
import { Textarea } from "@/components/Atoms/Textarea";
import { Card } from "@/components/Molecules/Card";
import { SegmentedControl } from "@/components/Molecules/SegmentedControl";

const styleOptions = [
  { label: "Directness", value: "directness" },
  { label: "Softness", value: "softness" },
  { label: "Politeness", value: "politeness" },
];

// Define the props for the controlled component
interface TransformStyleCardProps {
  inputValue: string;
  onInputChange: (value: string) => void;
  selectedStyleValue: string;
  onSelectedStyleChange: (value: string) => void;
  outputValue: string;
  onTransformClick: () => void;
  isTransformDisabled: boolean;
}

export const TransformStyleCard = ({
  inputValue,
  onInputChange,
  selectedStyleValue,
  onSelectedStyleChange,
  outputValue,
  onTransformClick,
  isTransformDisabled,
}: TransformStyleCardProps) => {
  return (
    <div className="flex flex-col items-center justify-center gap-8 lg:flex-row lg:gap-[58px]">
      <Card variant="primary" size="large">
        <div className="flex flex-col py-[9px] justify-between h-full">
          <Textarea
            value={inputValue}
            onChange={(e) => onInputChange(e.target.value)}
            placeholder="Enter your text"
            rows={8}
          />
          <Button
            size="xl"
            onClick={onTransformClick}
            disabled={isTransformDisabled}
          >
            Transform
          </Button>
        </div>
      </Card>

      <div className="flex flex-col gap-13">
        <SegmentedControl
          options={styleOptions}
          value={selectedStyleValue}
          onChange={onSelectedStyleChange}
        />
        <Card variant="primary" size="medium">
          <div className="flex justify-center">
            <Textarea
              value={outputValue}
              placeholder="Transformed text will appear here"
              readOnly
              rows={8}
            />
          </div>
        </Card>
      </div>

      <div className="flex justify-end mt-6"></div>
    </div>
  );
};