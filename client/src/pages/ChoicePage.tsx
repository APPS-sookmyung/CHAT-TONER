import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ChipGroup } from "@/components/Molecules/Chipgroup";
import { Modal } from "@/components/Molecules/Modal";
import { Button } from "@/components/Atoms/Button";
import type { UserProfile } from "@shared/schema";
import { PATH } from "@/constants/paths";

export default function ChoicePage() {
  const navigate = useNavigate();

  // State for the modal and profile
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const [profile, setProfile] = useState<UserProfile | null>(null);

  // Check for profile in localStorage when the page loads
  useEffect(() => {
    const profileString = localStorage.getItem("chatToner_profile");
    if (profileString) {
      setProfile(JSON.parse(profileString));
    }
    // Open the modal after checking
    setIsProfileModalOpen(true);
  }, []);

  const handleGoToSurvey = () => {
    setIsProfileModalOpen(false);
    navigate(PATH.SURVEY(1)); // Navigate to the first step of the survey
  };

  const handleGoToUpload = () => {
    setIsProfileModalOpen(false);
    navigate(PATH.UPLOAD); // Navigate to the upload page
  };

  // Original page data...
  const styleChips = [
    { label: "directness", colorScheme: "yellow" as const },
    { label: "softness", colorScheme: "yellow" as const },
    { label: "politeness", colorScheme: "yellow" as const },
    { label: "clarity", colorScheme: "yellow" as const },
    { label: "consistency", colorScheme: "yellow" as const },
    { label: "formality", colorScheme: "yellow" as const },
    { label: "conciseness", colorScheme: "yellow" as const },
    { label: "empathy", colorScheme: "yellow" as const },
  ];
  const qualityChips = [
    { label: "compliance", colorScheme: "purple" as const },
    { label: "grammar", colorScheme: "purple" as const },
    { label: "formality", colorScheme: "purple" as const },
    { label: "accuracy", colorScheme: "purple" as const },
    { label: "readability", colorScheme: "purple" as const },
    { label: "consistency", colorScheme: "purple" as const },
    { label: "clarity", colorScheme: "purple" as const },
    { label: "protocol", colorScheme: "purple" as const },
    { label: "professionalism", colorScheme: "purple" as const },
  ];

  return (
    <div className="flex items-center justify-center flex-grow">
      <div className="flex flex-row items-center gap-20">
        <div className="pt-4">
          <h1 className="items-center font-bold leading-tight text-black text-7xl">
            Use Chat Toner <br />
            for your <span className="text-primary">workflow</span>
          </h1>
        </div>
        <div className="flex flex-col gap-8">
          <Link
            to={PATH.TRANSFORM_STYLE}
            className="block transition-transform duration-200 ease-in-out hover:scale-105"
          >
            <ChipGroup
              title="Transform Style"
              chips={styleChips}
              variant="primary"
              size="small"
            />
          </Link>
          <Link
            to={PATH.ANALYZE_QUALITY}
            className="block transition-transform duration-200 ease-in-out hover:scale-105"
          >
            <ChipGroup
              title="Analyze Quality"
              chips={qualityChips}
              variant="primary"
              size="small"
            />
          </Link>
        </div>
      </div>

      {/* Modal for profile check */}
      <Modal
        isOpen={isProfileModalOpen}
        onClose={() => setIsProfileModalOpen(false)}
      >
        {profile ? (
          // Case 1: Profile EXISTS
          <div className="flex flex-col items-center justify-center h-full text-center">
            <h2 className="text-3xl font-bold">Welcome Back!</h2>
            <p className="mt-4 text-lg">
              A tone profile is already set up. You can continue using it, or
              create a new one.
            </p>
            <div className="flex justify-center gap-4 mt-8">
              <Button
                variant="secondary"
                size="md"
                onClick={() => setIsProfileModalOpen(false)}
              >
                Continue
              </Button>
              <Button variant="primary" size="md" onClick={handleGoToSurvey}>
                Update Profile
              </Button>
            </div>
          </div>
        ) : (
          // Case 2: Profile DOES NOT EXIST
          <div className="flex flex-col items-center justify-center h-full text-center">
            <h2 className="text-3xl font-bold">Set Up Your Tone Profile</h2>
            <p className="mt-4 text-lg">
              To get the most out of Chat Toner, you need to set up your tone
              profile first.
            </p>
            <div className="flex justify-center gap-4 mt-8">
              <Button variant="secondary" size="md" onClick={handleGoToUpload}>
                Upload Document
              </Button>
              <Button variant="primary" size="md" onClick={handleGoToSurvey}>
                Go to Survey
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
