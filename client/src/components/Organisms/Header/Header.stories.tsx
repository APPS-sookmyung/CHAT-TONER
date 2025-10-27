import type { Meta, StoryObj } from "@storybook/react";
import { Header } from "./index";

const meta: Meta<typeof Header> = {
  title: "Organisms/Header",
  component: Header,
  tags: ["autodocs"],
  argTypes: {
    isModalOpen: {
      control: "boolean",
      description: "모달이 열린 상태인지 여부",
    },
    onProfileClick: {
      action: "onProfileClick",
      description: "프로필 아이콘 클릭 이벤트 핸들러",
    },
  },
};

export default meta;
type Story = StoryObj<typeof Header>;

export const ModalClosed: Story = {
  args: {
    isModalOpen: false,
  },
};

export const ModalOpen: Story = {
  args: {
    isModalOpen: true,
  },
};
