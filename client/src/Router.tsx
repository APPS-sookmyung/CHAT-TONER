import { Routes, Route } from "react-router-dom";
import { PATH } from "@/constants/paths";

import LandingPage from "./pages/LandingPage";
import ChoicePage from "./pages/ChoicePage";
import TransformStylePage from "./pages/TransformStylePage";
import AnalyzeQualityPage from "./pages/AnalyzeQualityPage";
import SurveyPage from "./pages/SurveyPage";
import MainLayout from "./components/Templates/MainLayout";
import ResultsPage from "./pages/ResultsPage";
import UploadPage from "./pages/UploadPage";

const Router = () => {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path={PATH.HOME} element={<LandingPage />} />
        <Route path={PATH.CHOICE} element={<ChoicePage />} />
        <Route path={PATH.TRANSFORM_STYLE} element={<TransformStylePage />} />
        <Route path={PATH.ANALYZE_QUALITY} element={<AnalyzeQualityPage />} />
        <Route path={PATH.SURVEY(":step")} element={<SurveyPage />} />
        <Route path={PATH.RESULTS} element={<ResultsPage />} />
        <Route path={PATH.UPLOAD} element={<UploadPage />} />
      </Route>
    </Routes>
  );
};

export default Router;
