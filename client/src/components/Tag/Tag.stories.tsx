import type { Meta, StoryObj } from "@storybook/react";
import { Tag } from "./index";

const meta: Meta<typeof Tag> = {
  title: "Components/Tag",
  component: Tag,
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
type Story = StoryObj<typeof Tag>;

// 노란색 태그 스토리
export const YellowChip: Story = {
  args: {
    variant: "chip",
    colorScheme: "yellow",
    children: "Clarity",
  },
};

// 보라색 태그 스토리
export const PurpleChip: Story = {
  args: {
    variant: "chip",
    colorScheme: "purple",
    children: "Grammar",
  },
};
