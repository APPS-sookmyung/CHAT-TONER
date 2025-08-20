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
        // 404 에러는 정상적인 상황이므로 로그 출력하지 않음
        if (!error.message.includes('404')) {
          console.error("Failed to fetch profile:", error);
        }
        const raw = localStorage.getItem("chatToner_profile");
        if (raw) {
          try {
            const parsed = JSON.parse(raw);
            // 잘못된 프로필 형식인지 체크
            if (!parsed.responses || !parsed.responses.abbreviation_usage) {
              console.log('잘못된 프로필 형식, localStorage 초기화');
              localStorage.removeItem("chatToner_profile");
              return null;
            }
            return parsed;
          } catch (e) {
            localStorage.removeItem("chatToner_profile");
            return null;
          }
        }
        return null;
      }
    },
    enabled: Boolean(userId), 
    staleTime: Infinity, 
    cacheTime: Infinity,
  });

  const createDefaultProfile = () => {
    const defaultProfile = {
      id: 1,
      userId,
      baseFormalityLevel: 3,
      baseFriendlinessLevel: 3,
      baseEmotionLevel: 3,
      baseDirectnessLevel: 3,
      responses: {
        formality_level: 3,
        friendliness_level: 3,
        emotion_level: 3,
        directness_level: 3,
        uses_abbreviations: false,
        uses_emoticons: false,
        gratitude_expressions: ["감사합니다"],
        request_expressions: ["부탁드립니다"],
        situation_responses: {},
        // analyzeUserProfile이 기대하는 필드들
        abbreviation_usage: ["보통 사용"],
        emoticon_usage: ["보통 사용"],
        gratitude_senior: ["감사합니다"],
        request_colleague: ["부탁드립니다"],
        closing_expressions: ["감사합니다"],
        agreement_expressions: ["네, 맞습니다"]
      },
      completedAt: new Date(),
      createdAt: new Date().toISOString()
    };
    return defaultProfile;
  };

  const handleModeSelect = async (mode: "transform" | "validate") => {
    if (mode === "transform") {
      if (!profile) {
        // 기본 프로필 생성 및 저장
        const newProfile = createDefaultProfile();
        
        try {
          // 백엔드에 프로필 저장 시도
          const response = await fetch('/api/profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              userId,
              baseFormalityLevel: 3,
              baseFriendlinessLevel: 3,
              baseEmotionLevel: 3,
              baseDirectnessLevel: 3
            })
          });
          
          if (response.ok) {
            console.log('백엔드에 프로필 저장 완료');
          }
        } catch (error) {
          console.log('백엔드 프로필 저장 실패, localStorage만 사용');
        }
        
        // localStorage에 저장 (확실하게)
        localStorage.setItem("chatToner_profile", JSON.stringify(newProfile));
        console.log('기본 프로필 localStorage에 저장 완료:', newProfile);
        
        // 페이지 새로고침으로 프로필 다시 로드
        window.location.reload();
        return;
      }
      
      setLoc("/converter");
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
