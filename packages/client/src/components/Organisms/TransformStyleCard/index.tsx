import { useState } from "react";
import { Copy, Check } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
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
    <div className="flex flex-col items-stretch gap-8 lg:flex-row lg:gap-[58px] w-full max-w-7xl">
      <Card variant="primary" size="large" className="flex-1 flex flex-col">
        <div className="flex flex-col py-1 justify-between h-full flex-1">
          <Textarea
            value={inputValue}
            onChange={(e) => onInputChange(e.target.value)}
            placeholder="Enter your text"
            rows={8}
            className="flex-1"
          />
          <Button
            size="xl"
            onClick={onTransformClick}
            disabled={isTransformDisabled}
            className="mt-4"
          >
            Transform
          </Button>
        </div>
      </Card>

      <div className="flex flex-col gap-6 flex-1 items-stretch">
        <SegmentedControl
          options={styleOptions}
          value={selectedStyleValue}
          onChange={onSelectedStyleChange}
          className="w-full"
        />
        <Card variant="primary" size="large" className="flex-1 flex flex-col">
          <div className="relative">
            {outputValue && outputValue !== "Transformed text will appear here" ? (
              <div className="w-full min-h-[300px] flex-1 overflow-y-auto p-6 bg-white rounded-[20px] border border-primary text-sm text-text-primary prose prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{outputValue}</ReactMarkdown>
              </div>
            ) : (
              <div className="w-full min-h-[300px] flex-1 p-6 bg-white rounded-[20px] border border-primary text-sm text-text-secondary flex items-center justify-center">
                Transformed text will appear here
              </div>
            )}
            {outputValue && outputValue !== "Transformed text will appear here" && (
              <button
                onClick={handleCopy}
                className="absolute top-4 right-4 p-1.5 rounded-md bg-white/80 hover:bg-gray-100 transition-colors border border-gray-200 z-10"
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