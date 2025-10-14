import type { Meta, StoryObj } from "@storybook/react";
import { ChoiceCard } from "./index";

const meta: Meta<typeof ChoiceCard> = {
  title: "Atoms/ChoiceCard",
  component: ChoiceCard,
  tags: ["autodocs"],
  argTypes: {
    isSelected: { control: "boolean" },
    size: {
      control: "radio",
      options: ["sm", "lg"],
    },
    children: { control: "text" },
  },
};

export default meta;
type Story = StoryObj<typeof ChoiceCard>;

export const Small: Story = {
  args: {
    children: "Friendly",
    size: "sm",
    isSelected: false,
  },
};

export const SmallSelected: Story = {
  args: {
    ...Small.args,
    isSelected: true,
  },
};

export const Large: Story = {
  args: {
    children: "Internal Team Members",
    size: "lg",
    isSelected: false,
  },
};

export const LargeSelected: Story = {
  args: {
    ...Large.args,
    isSelected: true,
  },
};
