import type { Meta, StoryObj } from "@storybook/react";
import { Card } from "./index";

const meta: Meta<typeof Card> = {
  title: "molecules/Card",
  component: Card,
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: "select",
      options: ["primary", "secondary"],
    },
    size: {
      control: "select",
      options: ["small", "medium", "large"],
    },
  },
  args: {
    children: "Card Content Here",
  },
};

export default meta;
type Story = StoryObj<typeof Card>;

export const Default: Story = {};

// Primary variant
export const Primary: Story = {
  render: (args) => (
    <div className="flex flex-col items-start gap-4">
      <Card {...args} variant="primary" size="small">
        Primary Small (w-[574px] h-[334px])
      </Card>
      <Card {...args} variant="primary" size="medium">
        Primary Medium (w-[642px] h-[489px])
      </Card>
      <Card {...args} variant="primary" size="large">
        Primary Large (w-[642px] h-[615px])
      </Card>
    </div>
  ),
};

// Secondary variant
export const Secondary: Story = {
  render: (args) => (
    <div className="flex flex-col items-start gap-4">
      <Card {...args} variant="secondary" size="small">
        Secondary Small (w-[880px] h-[118px])
      </Card>
      <Card {...args} variant="secondary" size="medium">
        Secondary Medium (w-[880px] h-[435px])
      </Card>
    </div>
  ),
};
