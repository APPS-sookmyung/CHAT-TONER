import type { Meta, StoryObj } from "@storybook/react";
import { Chip } from "./index";

const meta: Meta<typeof Chip> = {
  title: "atoms/Chip",
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

export const YellowChip: Story = {
  args: {
    colorScheme: "yellow",
    children: "Clarity",
  },
};

export const PurpleChip: Story = {
  args: {
    colorScheme: "purple",
    children: "Grammar",
  },
};
