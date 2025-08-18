// src/App.tsx
import { Switch, Route } from "wouter";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/queryClient";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/toaster";

import ModeSelectPage from "@/pages/ModeSelectPage";
import QuestionnairePage from "@/pages/QuestionnairePage";
import ResultsPage from "@/pages/ResultsPage";
import ConverterPage from "@/pages/ConverterPage";
import ValidatePage from "@/pages/ValidatePage";
import TestPage from "@/pages/TestPage";
import NotFound from "@/pages/not-found";
import Layout from "@/pages/layout";

function Router() {
  return (
    <Layout>
      <Switch>
        <Route path="/" component={ModeSelectPage} />
        <Route path="/questionnaire" component={QuestionnairePage} />
        <Route path="/results" component={ResultsPage} />
        <Route path="/converter" component={ConverterPage} />
        <Route path="/validate" component={ValidatePage} />
        <Route path="/test" component={TestPage} />
      </Switch>
    </Layout>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Router />
      </TooltipProvider>
    </QueryClientProvider>
  );
}
