import type { Preview } from "@storybook/react-vite";
import "../src/index.css";

const style = document.createElement("style");
style.textContent = `
  :root {
    --color-primary: #10b981;
    --color-primary-foreground: #ffffff;
    --color-secondary: #d9d9d9;
    --color-surface: #f7f7f7;
    --color-text-primary: #000000;
    --color-text-secondary: #9da3af;
    --color-feature-secondary: #fef3aa;
    --color-feature-primary: #e9d5ff;
    --color-accent: #b7ead9;
  }
`;
document.head.appendChild(style);

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },

    a11y: {
      // 'todo' - show a11y violations in the test UI only
      // 'error' - fail CI on a11y violations
      // 'off' - skip a11y checks entirely
      test: "todo",
    },
  },
};

export default preview;
