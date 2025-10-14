import { useState } from "react";
import { Button } from "@/components/Atoms/Button";
import { Textarea } from "@/components/Atoms/Textarea";
import { Card } from "@/components/Molecules/Card";
import { SegmentedControl } from "@/components/Molecules/SegmentedControl";

const styleOptions = [
  { label: "Directness", value: "directness" },
  { label: "Softness", value: "softness" },
  { label: "Politeness", value: "politeness" },
];

export const TransformStyleCard = () => {
  const [inputText, setInputText] = useState("");
  const [selectedStyle, setSelectedStyle] = useState(styleOptions[0].value);
  const [outputText, setOutputText] = useState("");

  const handleTransform = () => {
    setOutputText(
      `Transformed text for '${inputText}' with style '${selectedStyle}'`
    );
  };

  return (
    <div className="flex flex-row gap-[58px]">
      <Card variant="primary" size="large">
        <div className="flex flex-col py-[9px] justify-between h-full">
          <Textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Enter your text"
            rows={8}
          />
          <Button size="xl" onClick={handleTransform}>
            Transform
          </Button>
        </div>
      </Card>

      <div className="flex flex-col gap-13">
        <SegmentedControl
          options={styleOptions}
          value={selectedStyle}
          onChange={setSelectedStyle}
        />
        <Card variant="primary" size="medium">
          <div className="flex justify-center">
            <Textarea
              value={outputText}
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
