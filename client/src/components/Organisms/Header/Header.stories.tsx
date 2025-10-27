import type { Meta, StoryObj } from "@storybook/react";
import { Header } from "./index";

const meta: Meta<typeof Header> = {
  title: "Organisms/Header",
  component: Header,
  tags: ["autodocs"],
  parameters: {
    docs: {
      description: {
        component:
          "Header component with integrated profile management. Manages modal state internally and handles user profile loading from localStorage.",
      },
    },
  },
};

export default meta;
type Story = StoryObj<typeof Header>;

export const Default: Story = {
  parameters: {
    docs: {
      description: {
        story:
          "Default header with profile management functionality. Click the profile icon to toggle the dropdown modal.",
      },
    },
  },
};

export const WithUserProfile: Story = {
  parameters: {
    docs: {
      description: {
        story:
          "Header when user profile data is available in localStorage. The profile dropdown will show actual user data.",
      },
    },
  },
};
