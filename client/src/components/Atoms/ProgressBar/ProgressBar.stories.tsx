import type { Meta, StoryObj } from "@storybook/react";
import { ProgressBar } from "./index";

const meta: Meta<typeof ProgressBar> = {
  title: "Atoms/ProgressBar",
  component: ProgressBar,
  tags: ["autodocs"],
  argTypes: {
    label: { control: "text" },
    currentStep: { control: { type: "number", min: 0 } },
    totalSteps: { control: { type: "number", min: 1 } },
  },
};

export default meta;
type Story = StoryObj<typeof ProgressBar>;

export const Default: Story = {
  args: {
    label: "Tone Profile Setup",
    currentStep: 4,
    totalSteps: 11,
  },
};

export const Start: Story = {
  args: {
    label: "Tone Profile Setup",
    currentStep: 1,
    totalSteps: 11,
  },
};

export const Complete: Story = {
  args: {
    label: "Tone Profile Setup",
    currentStep: 11,
    totalSteps: 11,
  },
};
