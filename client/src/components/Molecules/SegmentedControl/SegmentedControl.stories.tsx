import type { Meta, StoryObj } from "@storybook/react";
import { useState } from "react";
import { SegmentedControl } from "./index";

const meta: Meta<typeof SegmentedControl> = {
  title: "molecules/SegmentedControl",
  component: SegmentedControl,
  tags: ["autodocs"],
  argTypes: {
    options: { control: false },
    value: { control: false },
    onChange: { control: false },
  },
};

export default meta;
type Story = StoryObj<typeof SegmentedControl>;

// Analyze Quality
const qualityOptions = [
  { label: "Grammar", value: "grammar" },
  { label: "Formality", value: "formality" },
  { label: "Protocol", value: "protocol" },
];

// Transform Style
const styleOptions = [
  { label: "Directness", value: "directness" },
  { label: "Softness", value: "softness" },
  { label: "Politeness", value: "politeness" },
];

export const AnalyzeQuality: Story = {
  name: "For Analyze Quality",
  render: () => {
    const [selectedValue, setSelectedValue] = useState(qualityOptions[0].value);

    return (
      <div style={{ width: "642px" }}>
        <SegmentedControl
          options={qualityOptions}
          value={selectedValue}
          onChange={setSelectedValue}
        />
        <p className="mt-4 text-center">
          Selected Value: <strong>{selectedValue}</strong>
        </p>
      </div>
    );
  },
};

export const TransformStyle: Story = {
  name: "For Transform Style",
  render: () => {
    const [selectedValue, setSelectedValue] = useState(styleOptions[0].value);

    return (
      <div style={{ width: "642px" }}>
        <SegmentedControl
          options={styleOptions}
          value={selectedValue}
          onChange={setSelectedValue}
        />
        <p className="mt-4 text-center">
          Selected Value: <strong>{selectedValue}</strong>
        </p>
      </div>
    );
  },
};
