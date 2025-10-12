import type { Meta, StoryObj } from "@storybook/react";
import { ChipGroup } from "./index";

const meta: Meta<typeof ChipGroup> = {
  title: "Molecules/ChipGroup",
  component: ChipGroup,
  tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof ChipGroup>;

type Chip = { label: string; colorScheme: "yellow" | "purple" };

const styleChips: Chip[] = [
  { label: "directness", colorScheme: "yellow" },
  { label: "softness", colorScheme: "yellow" },
  { label: "politeness", colorScheme: "yellow" },
  { label: "clarity", colorScheme: "yellow" },
  { label: "consistency", colorScheme: "yellow" },
  { label: "formality", colorScheme: "yellow" },
  { label: "conciseness", colorScheme: "yellow" },
  { label: "empathy", colorScheme: "yellow" },
];
const qualityChips: Chip[] = [
  { label: "compliance", colorScheme: "purple" },
  { label: "grammar", colorScheme: "purple" },
  { label: "formality", colorScheme: "purple" },
  { label: "accuracy", colorScheme: "purple" },
  { label: "readability", colorScheme: "purple" },
  { label: "consistency", colorScheme: "purple" },
  { label: "clarity", colorScheme: "purple" },
  { label: "protocol", colorScheme: "purple" },
  { label: "professionalism", colorScheme: "purple" },
];

export const TransformStyle: Story = {
  args: {
    title: "Transform Style",
    chips: styleChips,
    variant: "primary", // Card variant
    size: "small", // Card size
  },
};

export const AnalyzeQuality: Story = {
  args: {
    title: "Analyze Quality",
    chips: qualityChips,
    variant: "primary", // Card variant
    size: "small", // Card size
  },
};
