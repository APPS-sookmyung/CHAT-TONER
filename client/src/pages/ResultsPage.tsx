import { useEffect, useState } from "react";
import ResultsSummary from "@/components/questionnaire/results-summary";
import type { UserProfile } from "@shared/schema";
import { useNavigate } from "react-router-dom";

export default function ResultsPage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);

  useEffect(() => {
    const raw = localStorage.getItem("chatToner_profile");
    if (raw) setProfile(JSON.parse(raw));
  }, []);

  if (!profile) return null;

  return (
    <main className="max-w-6xl p-8 mx-auto">
      <ResultsSummary
        userProfile={profile}
        completionRate={100}
        onStartConversion={() => navigate("/validate")}
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
