export interface Question {
  id: string;
  category: "company_profile" | "communication_style";
  categoryLabel: string;
  question: string;
  description: string;
  options: string[];
  allowMultiple: boolean;
  allowCustom: boolean;
}

export const questions: Question[] = [
  {
    id: "company_name",
    category: "company_profile",
    categoryLabel: "Company Profile",
    question: "What is your company or team name?",
    description: "Please enter the name of your organization to help us personalize your experience",
    options: [],
    allowMultiple: false,
    allowCustom: true,
  },
  {
    id: "team_size",
    category: "company_profile",
    categoryLabel: "Company Profile",
    question: "How many members are on your team?",
    description: "Enter a number representing the total size of your immediate team.",
    options: [],
    allowMultiple: false,
    allowCustom: true,
  },
  {
    id: "communication_style",
    category: "communication_style",
    categoryLabel: "Communication Style",
    question: "Which of the following best describes your team’s communication style?",
    description: "",
    options: ["Friendly", "Strictly", "Formal", "Casual"],
    allowMultiple: false,
    allowCustom: false,
  },
  {
    id: "internal_communication_tool",
    category: "communication_style",
    categoryLabel: "Communication Style",
    question: "What is your primary tool for internal communication?",
    description: "",
    options: ["Slack", "Discord", "Microsoft Teams", "Google Chat", "Email"],
    allowMultiple: false,
    allowCustom: true,
  },
  {
    id: "main_audience",
    category: "communication_style",
    categoryLabel: "Communication Style",
    question: "Who is your main audience when you communicate?",
    description: "",
    options: ["Internal Team Members", "External Clients/Customers", "Other Departments", "partners/vendors", "c-level Executives"],
    allowMultiple: false,
    allowCustom: false,
  },
];

export const getQuestionsByCategory = (category: Question["category"]) => {
  return questions.filter((q) => q.category === category);
};

export const getCategoryProgress = (
  category: Question["category"],
  responses: Record<string, any>
) => {
  const categoryQuestions = getQuestionsByCategory(category);
  const answeredQuestions = categoryQuestions.filter((q) => responses[q.id]);
  return {
    answered: answeredQuestions.length,
    total: categoryQuestions.length,
    percentage: Math.round(
      (answeredQuestions.length / categoryQuestions.length) * 100
    ),
  };
};