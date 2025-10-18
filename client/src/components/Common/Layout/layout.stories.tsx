import type { Meta, StoryObj } from "@storybook/react";
import Layout from "./index";
import { MemoryRouter, Route, Routes } from "react-router-dom";

const MockPage = () => (
  <div style={{ padding: "100px" }}>
    <h1>Try Chat Toner</h1>
    <p>An AI-powered tool to unify styles across your team</p>
  </div>
);

const meta: Meta<typeof Layout> = {
  title: "Common/Layout",
  component: Layout,
  decorators: [
    (Story) => (
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route element={<Story />}>
            <Route path="/" element={<MockPage />} />
          </Route>
        </Routes>
      </MemoryRouter>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
