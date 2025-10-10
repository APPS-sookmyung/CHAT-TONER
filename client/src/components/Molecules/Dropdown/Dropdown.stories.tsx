import type { Meta, StoryObj } from "@storybook/react";
import { useState } from "react";
import { Dropdown } from "./index";

const meta: Meta<typeof Dropdown> = {
  title: "Molecules/Dropdown",
  component: Dropdown,
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: "radio",
      options: ["situation", "target"],
    },
    size: {
      control: "radio",
      options: ["default", "compact"],
    },
  },
};

export default meta;
type Story = StoryObj<typeof Dropdown>;

const situationOptions = [
  { label: "Report", value: "report" },
  { label: "Meeting Minutes", value: "meeting-minutes" },
  { label: "Email", value: "email" },
  { label: "Announcement", value: "announcement" },
  { label: "Instant Message / Chat", value: "message" },
];
const targetOptions = [
  { label: "Teammate / Colleague", value: "teammate" },
  { label: "Another Department", value: "cross-functional" },
  { label: "Client", value: "client" },
  { label: "External Partner / Vendor", value: "vendor" },
  { label: "Junior Colleague / New Hire", value: "junior" },
];

const InteractiveDropdown = (args: any) => {
  const [selectedValue, setSelectedValue] = useState<string | undefined>();

  return (
    <div style={{ width: "320px" }}>
      <Dropdown {...args} value={selectedValue} onChange={setSelectedValue} />
      <p className="mt-4">
        Selected Value: <strong>{selectedValue || "None"}</strong>
      </p>
    </div>
  );
};

export const Situation: Story = {
  args: {
    variant: "situation",
    size: "default",
    options: situationOptions,
    placeholder: "Select a situation",
  },
  render: InteractiveDropdown,
};

export const Target: Story = {
  args: {
    variant: "target",
    size: "compact",
    options: targetOptions,
    placeholder: "Select a target",
  },
  render: InteractiveDropdown,
};
