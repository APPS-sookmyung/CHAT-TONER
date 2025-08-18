import { useEffect, useState } from "react";
import ModeSelector from "@/components/mode-selector";
import type { UserProfile } from "@shared/schema";
import { Link, useLocation } from "wouter";
import { MessageSquare } from "lucide-react";

const USER_ID_KEY = "chatToner_userId";
const getUserId = () => {
  let id = localStorage.getItem(USER_ID_KEY);
  if (!id) {
    id = crypto?.randomUUID?.() ?? `user_${Date.now()}`;
    localStorage.setItem(USER_ID_KEY, id);
  }
  return id;
};

export default function ModeSelectPage() {
  const [, setLoc] = useLocation();
  const userId = getUserId();
  const [profile, setProfile] = useState<UserProfile | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`/api/profile/${userId}`);
        if (res.ok) {
          const p = await res.json();
          setProfile(p);
        } else {
          const raw = localStorage.getItem("chatToner_profile");
          if (raw) setProfile(JSON.parse(raw));
        }
      } catch {
        const raw = localStorage.getItem("chatToner_profile");
        if (raw) setProfile(JSON.parse(raw));
      }
    })();
  }, [userId]);

  const handleModeSelect = (mode: "transform" | "validate") => {
    if (mode === "transform") {
      setLoc(profile ? "/converter" : "/questionnaire");
    } else {
      setLoc("/validate");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 font-korean">
      <main className="max-w-6xl mx-auto p-8">
        <ModeSelector onModeSelect={handleModeSelect} />
      </main>
    </div>
  );
}
