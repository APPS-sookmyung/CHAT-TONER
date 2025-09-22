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
import NotFound from "@/pages/not-found";
import Layout from "@/pages/layout";

function Router() {
  return (
    <Layout>
      <Switch>
        {/* 홈페이지 (모드 선택) */}
        <Route path="/" component={HomePage} />

        {/* 스타일 정의 (설문 페이지) */}
        <Route path="/style-definition" component={QuestionnairePage} />

        {/* 스타일 분석 결과 */}
        <Route path="/style-definition/results" component={ResultsPage} />

        {/* 스타일 변환기 */}
        <Route path="/style-conversion" component={ConverterPage} />

        {/* 품질 분석기 */}
        <Route path="/quality-analysis" component={ValidatePage} />

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
