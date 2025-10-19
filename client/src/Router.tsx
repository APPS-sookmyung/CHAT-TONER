import { Routes, Route } from "react-router-dom";
import { ROUTES } from "./constants/routes";

// Import existing pages
import HomePage from "@/pages/home";
import QuestionnairePage from "@/pages/QuestionnairePage";
import ResultsPage from "@/pages/ResultsPage";
import ConverterPage from "@/pages/ConverterPage";
import ValidatePage from "@/pages/ValidatePage";
import UploadPage from "@/pages/UploadPage";
import NotFound from "@/pages/not-found";
import Layout from "@/pages/layout";

const Router = () => {
  return (
    <Layout>
      <Routes>
        <Route path={ROUTES.HOME} element={<HomePage />} />
        <Route path={ROUTES.QUESTIONNAIRE} element={<QuestionnairePage />} />
        <Route path={ROUTES.UPLOAD} element={<UploadPage />} />
        <Route path={ROUTES.RESULTS} element={<ResultsPage />} />
        <Route path={ROUTES.CONVERTER} element={<ConverterPage />} />
        <Route path={ROUTES.VALIDATE} element={<ValidatePage />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Layout>
  );
};

export default Router;