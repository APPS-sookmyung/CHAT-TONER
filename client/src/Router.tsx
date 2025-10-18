import { BrowserRouter, Routes, Route } from "react-router-dom";
import { PATH } from "@/constants/paths"; // 1. 경로 상수(사전) 가져오기

// Pages
import LandingPage from "./pages/LandingPage";
import ChoicePage from "./pages/ChoicePage";
import TransformStylePage from "./pages/TransformStylePage";
import AnalyzeQualityPage from "./pages/AnalyzeQualityPage";
import SurveyPage from "./pages/SurveyPage";
import Layout from "./components/Common/Layout";

const Router = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path={PATH.HOME} element={<LandingPage />} />
          <Route path={PATH.CHOICE} element={<ChoicePage />} />
          <Route path={PATH.TRANSFORM_STYLE} element={<TransformStylePage />} />
          <Route path={PATH.ANALYZE_QUALITY} element={<AnalyzeQualityPage />} />
          <Route path={PATH.SURVEY(":step")} element={<SurveyPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default Router;
