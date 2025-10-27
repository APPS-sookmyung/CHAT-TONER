import type { Meta, StoryObj } from "@storybook/react";
import { Input } from "./";

const meta: Meta<typeof Input> = {
  title: "Atoms/Input",
  component: Input,
  tags: ["autodocs"],
  argTypes: {
    placeholder: { control: "text" },
    disabled: { control: "boolean" },
  },
};

export default meta;
type Story = StoryObj<typeof Input>;

export const Default: Story = {
  args: {
    placeholder: "Enter your company or team name...",
  },
};

export const Disabled: Story = {
  args: {
    placeholder: "This input is disabled",
    disabled: true,
  },
};

export const WithValue: Story = {
  args: {
    value: "Chat Toner",
  },
};
