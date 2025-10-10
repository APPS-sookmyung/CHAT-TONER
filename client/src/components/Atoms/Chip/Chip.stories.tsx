import type { Meta, StoryObj } from "@storybook/react";
import { Chip } from "./index";

const meta: Meta<typeof Chip> = {
  title: "Atoms/Chip",
  component: Chip,
  tags: ["autodocs"],
  argTypes: {
    colorScheme: {
      control: "radio",
      options: ["yellow", "purple"],
    },
    children: {
      control: "text",
    },
  },
};

export default meta;
type Story = StoryObj<typeof Chip>;

// 노란색 칩 스토리
export const YellowChip: Story = {
  args: {
    colorScheme: "yellow",
    children: "Clarity",
  },
};

// 보라색 칩 스토리
export const PurpleChip: Story = {
  args: {
    colorScheme: "purple",
    children: "Grammar",
  },
};
