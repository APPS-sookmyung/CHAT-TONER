import type { Meta, StoryObj } from "@storybook/react";
import { TransformStyleCard } from "./index";

const meta: Meta<typeof TransformStyleCard> = {
  title: "Organisms/TransformStyleCard",
  component: TransformStyleCard,
  tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof TransformStyleCard>;

export const Default: Story = {};
