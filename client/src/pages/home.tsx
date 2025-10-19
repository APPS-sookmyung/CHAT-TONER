import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { PencilRuler, Sparkles } from "lucide-react";
import { useState, useEffect } from "react";
import WelcomeModal from "@/components/welcome-modal";

export default function HomePage() {
  const navigate = useNavigate();
  const [hasProfile, setHasProfile] = useState<boolean | null>(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    // Check profile in localStorage
    let profileExists = false;
    try {
      const profile = localStorage.getItem("chatToner_profile");
      profileExists = Boolean(profile);
    } catch (error) {
      console.error("Error reading localStorage:", error);
      // Even if localStorage access fails, the modal should still be shown,
      // so profileExists remains false.
    }

    setHasProfile(profileExists);
    setShowModal(true); // Show modal immediately after profile check
  }, []);

  const handleStartQuestionnaire = () => {
    setShowModal(false);
    navigate("/questionnaire");
  };

  const handleStartUpload = () => {
    setShowModal(false);
    navigate("/upload");
  };

  const handleCloseModal = () => {
    setShowModal(false);
  };

  const handleStyleDefinitionClick = () => {
    try {
      const profile = localStorage.getItem("chatToner_profile");
      // If profile exists, go to converter. Otherwise, go to questionnaire.
      const targetUrl = profile ? "/converter" : "/questionnaire";
      navigate(targetUrl);
    } catch (error) {
      console.error("Error reading localStorage:", error);
      // Fallback to questionnaire if localStorage fails
      navigate("/questionnaire");
    }
  };

  return (
    <div className="space-y-12">
      {hasProfile !== null && (
        <WelcomeModal
          open={showModal}
          onClose={handleCloseModal}
          hasProfile={hasProfile}
          onStartQuestionnaire={handleStartQuestionnaire}
          onStartUpload={handleStartUpload}
        />
      )}
      {/* Hero section */}
      <div className="py-4 text-center">
        <h1 className="mb-6 text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
          An AI-powered tool to unify communication styles across your team{" "}
          <br />
          <span className="text-[#00C4B7]">Chat Toner</span>
        </h1>
        <p className="max-w-3xl mx-auto text-lg leading-relaxed text-gray-600 sm:text-xl md:text-2xl">
          Standardize team communication with style profiles <br />
          Reduce editing overhead with automated tone checks <br />
          Build trust with consistent brand voice
        </p>
      </div>

      {/* Mode select */}
      <div className="max-w-5xl px-4 mx-auto">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
          <Card className="p-2 transition-shadow hover:shadow-lg">
            <CardHeader>
              <div className="flex items-center gap-4">
                <PencilRuler className="w-10 h-10 text-[#00C4B7]" />
                <div>
                  <CardTitle className="text-2xl font-bold">
                    Style Definition
                  </CardTitle>
                  <CardDescription>
                    Define your own unique tone of voice through a survey
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="mb-6 text-lg text-gray-600">
                Create a personalized text style profile by answering a few
                questions. The AI learns your preferences for formality,
                friendliness, etc.
              </p>
              <Button
                onClick={handleStyleDefinitionClick}
                className="w-full py-3 text-lg"
              >
                Start Defining Style
              </Button>
            </CardContent>
          </Card>

          <Card className="p-2 transition-shadow hover:shadow-lg">
            <CardHeader>
              <div className="flex items-center gap-4">
                <Sparkles className="w-10 h-10 text-[#00C4B7]" />
                <div>
                  <CardTitle className="text-2xl font-bold">
                    Quality Conversion
                  </CardTitle>
                  <CardDescription>
                    Instantly improve the quality and tone of your Korean text
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="mb-6 text-lg text-gray-600">
                Paste your text and the AI will increase clarity, correct typos,
                and adjust the tone according to your base profile.
              </p>
              <Button
                onClick={() => navigate("/validate")}
                className="w-full py-3 text-lg"
              >
                Go to Analyzer
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
