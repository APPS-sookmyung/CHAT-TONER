// src/App.tsx
import { Switch, Route } from "wouter";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/queryClient";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/toaster";

import HomePage from "@/pages/home";
import QuestionnairePage from "@/pages/QuestionnairePage";
import ResultsPage from "@/pages/ResultsPage";
import ConverterPage from "@/pages/ConverterPage";
import ValidatePage from "@/pages/ValidatePage";
import UploadPage from "@/pages/UploadPage"; // Added
import NotFound from "@/pages/not-found";
import Layout from "@/pages/layout";

function Router() {
  return (
    <Layout>
      <Switch>
        {/* Homepage (mode selection) */}
        <Route path="/" component={HomePage} />

        {/* Style definition (questionnaire page) */}
        <Route path="/questionnaire" component={QuestionnairePage} />

        {/* Style definition (document upload) */}
        <Route path="/upload" component={UploadPage} />

        {/* 스타일 분석 결과 */}
        {/* Style analysis results */}
        <Route path="/results" component={ResultsPage} />

        {/* Style converter */}
        <Route path="/converter" component={ConverterPage} />

        {/* Quality analyzer */}
        <Route path="/validate" component={ValidatePage} />

        {/* 404 Not Found */}
        <Route component={NotFound} />
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
