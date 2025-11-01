import type { Meta, StoryObj } from "@storybook/react";
import { useState } from "react";
import { ChoiceGroup } from "./index";

const meta: Meta<typeof ChoiceGroup> = {
  title: "Molecules/ChoiceGroup",
  component: ChoiceGroup,
  tags: ["autodocs"],
  argTypes: {
    options: { control: false },
    value: { control: false },
    onChange: { control: false },
    size: { control: false },
  },
};

export default meta;
type Story = StoryObj<typeof ChoiceGroup>;

const smallOptions = [
  { label: "Friendly", value: "friendly" },
  { label: "Strict", value: "strict" },
  { label: "Formal", value: "formal" },
];

const largeOptions = [
  { label: "Internal Team Members", value: "internal" },
  { label: "Other Departments", value: "departments" },
  { label: "C-level Executives", value: "executives" },
  { label: "External Clients / Partners", value: "external" },
];

export const Small: Story = {
  render: () => {
    const [selectedValue, setSelectedValue] = useState(smallOptions[0].value);

    return (
      <ChoiceGroup
        options={smallOptions}
        value={selectedValue}
        onChange={setSelectedValue}
        size="sm"
      />
    );
  },
};

export const Large: Story = {
  render: () => {
    const [selectedValue, setSelectedValue] = useState(largeOptions[0].value);

    return (
      <ChoiceGroup
        options={largeOptions}
        value={selectedValue}
        onChange={setSelectedValue}
        size="lg"
      />
    );
  },
};
