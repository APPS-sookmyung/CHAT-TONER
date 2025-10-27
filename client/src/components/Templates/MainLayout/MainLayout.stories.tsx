import { Meta, StoryObj } from "@storybook/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import MainLayout from ".";

const meta: Meta<typeof MainLayout> = {
  title: "Templates/MainLayout",
  component: MainLayout,
};

export default meta;

type Story = StoryObj<typeof MainLayout>;

export const Default: Story = {
  render: () => (
    <MemoryRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route
            index
            element={<div>Your content goes here (via Outlet)</div>}
          />
        </Route>
      </Routes>
    </MemoryRouter>
  ),
};
