import { useState } from "react";
import { Copy, Check } from "lucide-react";
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
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!outputValue || outputValue === "Transformed text will appear here") return;
    await navigator.clipboard.writeText(outputValue);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

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
          <div className="relative">
            <Textarea
              value={outputValue}
              placeholder="Transformed text will appear here"
              readOnly
              rows={8}
            />
            {outputValue && outputValue !== "Transformed text will appear here" && (
              <button
                onClick={handleCopy}
                className="absolute top-2 right-2 p-1.5 rounded-md bg-white/80 hover:bg-gray-100 transition-colors border border-gray-200"
                title="Copy to clipboard"
              >
                {copied ? (
                  <Check className="h-4 w-4 text-green-500" />
                ) : (
                  <Copy className="h-4 w-4 text-gray-500" />
                )}
              </button>
            )}
          </div>
        </Card>
      </div>

      <div className="flex justify-end mt-6"></div>
    </div>
  );
};