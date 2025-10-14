import type { Meta, StoryObj } from "@storybook/react";
import { AnalyzeQualityCard } from "./index";

const meta: Meta<typeof AnalyzeQualityCard> = {
  title: "Organisms/AnalyzeQualityCard",
  component: AnalyzeQualityCard,
  tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof AnalyzeQualityCard>;

export const Default: Story = {};
