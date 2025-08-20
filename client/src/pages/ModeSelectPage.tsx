import { useEffect, useState } from "react";
import ModeSelector from "@/components/mode-selector";
import type { UserProfile } from "@shared/schema";
import { Link, useLocation } from "wouter";
import { MessageSquare } from "lucide-react";
import { API } from '@/lib/endpoints';
import { useQuery } from '@tanstack/react-query';
import { apiRequest } from '../lib/queryClient';

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
  const { data: profile } = useQuery<UserProfile | null>({ 
    queryKey: ['profile', userId],
    queryFn: async () => {
      if (!userId) return null; 
      try {
        const res = await apiRequest(API.profile(userId));
        const p = await res.json();
        return p;
      } catch (error) {
        console.error("Failed to fetch profile:", error);
        const raw = localStorage.getItem("chatToner_profile");
        return raw ? JSON.parse(raw) : null;
      }
    },
    enabled: Boolean(userId), 
    staleTime: Infinity, 
    cacheTime: Infinity,
  });

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
