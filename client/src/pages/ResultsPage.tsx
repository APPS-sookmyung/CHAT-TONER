import { useEffect, useState } from "react";
import ResultsSummary from "@/components/questionnaire/results-summary";
import type { UserProfile } from "@shared/schema";
import { useNavigate } from "react-router-dom";
import { PATH } from "@/constants/paths";

// Mock user profile for development when localStorage is empty
const createMockProfile = (): UserProfile => ({
  id: 1,
  baseFormalityLevel: 75,
  baseFriendlinessLevel: 60,
  baseEmotionLevel: 50,
  baseDirectnessLevel: 80,
  completedAt: new Date(),
  responses: {
    formality_level: 75,
    friendliness_level: 60,
    emotion_level: 50,
    directness_level: 80,
  },
});

export default function ResultsPage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);

  useEffect(() => {
    const raw = localStorage.getItem("chatToner_profile");
    if (raw) {
      setProfile(JSON.parse(raw));
    } else {
      // For development: if no profile in localStorage, use a mock one.
      console.warn(
        "No user profile found in localStorage. Using mock data for development."
      );
      setProfile(createMockProfile());
    }
  }, []);

  if (!profile) {
    return <div className="p-8 text-center">Loading profile...</div>;
  }

  return (
    <main className="max-w-6xl p-8 mx-auto">
      <ResultsSummary
        userProfile={profile}
        completionRate={100}
        onStartConversion={() => navigate(PATH.CHOICE)}
        onExportData={() => {
          const dataStr = JSON.stringify(profile, null, 2);
          const url = URL.createObjectURL(
            new Blob([dataStr], { type: "application/json" })
          );
          const a = document.createElement("a");
          a.href = url;
          a.download = "chat-toner-profile.json";
          a.click();
        }}
      />
    </main>
  );
}
