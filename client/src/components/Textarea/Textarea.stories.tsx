import type { Meta, StoryObj } from "@storybook/react";
import { Textarea } from "./index";

const meta: Meta<typeof Textarea> = {
  title: "Components/Textarea",
  component: Textarea,
  tags: ["autodocs"],
  argTypes: {
    readOnly: { control: "boolean" },
    placeholder: { control: "text" },
  },
};

export default meta;
type Story = StoryObj<typeof Textarea>;

export const Editable: Story = {
  args: {
    placeholder: "Enter your text here...",
    readOnly: false,
  },
};

export const ReadOnly: Story = {
  args: {
    value:
      "This is a read-only text area, typically used for displaying results.",
    readOnly: true,
  },
};
