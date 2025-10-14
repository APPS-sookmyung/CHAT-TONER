// src/components/organisms/AnalyzeQualityCard/index.tsx

import React, { useState } from "react";
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

export const AnalyzeQualityCard = () => {
  const [target, setTarget] = useState<string | undefined>();
  const [situation, setSituation] = useState<string | undefined>();
  const [quality, setQuality] = useState(qualityOptions[0].value);
  const [inputText, setInputText] = useState("");
  const [outputText, setOutputText] = useState("");

  const isButtonDisabled = inputText.trim() === "" || !target || !situation;

  const handleAnalyze = () => {
    setOutputText(
      `Analyzing text for target '${target}', situation '${situation}' with quality focus on '${quality}'.`
    );
  };

  return (
    <div className="flex flex-row gap-[58px]">
      <Card variant="primary" size="large">
        <div className="flex flex-col justify-between h-full">
          <div className="flex flex-col gap-4">
            <div className="flex gap-4">
              <Dropdown
                options={targetOptions}
                value={target}
                onChange={setTarget}
                placeholder="Target"
                variant="target"
                size="compact"
              />
              <Dropdown
                options={situationOptions}
                value={situation}
                onChange={setSituation}
                placeholder="Situation"
                variant="situation"
                size="default"
              />
            </div>
            <Textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Enter your text"
            />
          </div>

          <Button size="xl" onClick={handleAnalyze} disabled={isButtonDisabled}>
            Analyze
          </Button>
        </div>
      </Card>

      <div className="flex flex-col gap-13">
        <SegmentedControl
          options={qualityOptions}
          value={quality}
          onChange={setQuality}
        />
        <Card variant="primary" size="medium">
          <div className="flex items-center justify-center h-full">
            <Textarea
              value={outputText}
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
