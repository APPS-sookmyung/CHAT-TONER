import type { Meta, StoryObj } from "@storybook/react";
import ProfileDropdown from "./index";
import { Toaster } from "@/components/ui/toaster";

const meta: Meta<typeof ProfileDropdown> = {
  title: "Organisms/ProfileDropdown",
  component: ProfileDropdown,
  tags: ["autodocs"],
  decorators: [
    (Story) => (
      <div>
        <Story />
        <Toaster />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof ProfileDropdown>;

export const Default: Story = {
  args: {
    open: true,
    onClose: () => console.log("Close clicked"),
  },
};

export const Closed: Story = {
  args: {
    open: false,
  },
};
