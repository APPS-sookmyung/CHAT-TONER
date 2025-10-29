import type { Meta, StoryObj } from "@storybook/react";
import { MemoryRouter } from "react-router-dom";
import { SurveyStep, type Question } from "./";

const meta: Meta<typeof SurveyStep> = {
  title: "Organisms/SurveyStep",
  component: SurveyStep,
  decorators: [
    (Story) => (
      <MemoryRouter initialEntries={["/"]}>
        <Story />
      </MemoryRouter>
    ),
  ],
  tags: ["autodocs"],
  argTypes: {
    onNext: { action: "onNext clicked" },
    onPrev: { action: "onPrev clicked" },
  },
  parameters: {
    layout: 'centered',
  },
};

export default meta;
type Story = StoryObj<typeof SurveyStep>;

const textQuestion: Question = {
  number: 1,
  title: "What is your company or team name?",
  type: "text",
  placeholder: "Enter your answer here",
};

const choiceQuestion: Question = {
  number: 3,
  title:
    "Which of the following best describes your team's communication style?",
  type: "choice",
  options: [
    { label: "Friendly", value: "friendly" },
    { label: "Strict", value: "strict" },
    { label: "Formal", value: "formal" },
  ],
  choiceSize: "sm",
};

export const TextQuestion: Story = {
  args: {
    question: textQuestion,
    totalSteps: 5,
  },
};

export const ChoiceQuestion: Story = {
  args: {
    question: choiceQuestion,
    totalSteps: 5,
  },
};
