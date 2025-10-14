import type { Meta, StoryObj } from "@storybook/react";
import { Modal } from "./index";
import { ToneProfileModal } from "../../Toneprofile";

const meta: Meta<typeof Modal> = {
  title: "molecules/Modal",
  component: Modal,
  tags: ["autodocs"],
  argTypes: {
    isOpen: {
      control: "boolean",
      description: "Controls the open/close state of the modal.",
    },
    onClose: {
      action: "closed",
      description: "Function called when the modal is closed.",
    },
    children: {
      control: false,
      description: "React node to be rendered inside the modal.",
    },
  },
};

export default meta;
type Story = StoryObj<typeof Modal>;

export const Default: Story = {
  args: {
    isOpen: true,
    children: <div>Modal Content Example</div>,
  },
};

export const WithExistingToneProfile: Story = {
  args: {
    isOpen: true,
    children: <ToneProfileModal hasProfile={true} />,
  },
};

export const WithNewToneProfile: Story = {
  args: {
    isOpen: true,
    children: <ToneProfileModal hasProfile={false} />,
  },
};
