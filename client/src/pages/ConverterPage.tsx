import { useEffect, useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import ProfileSummary from "@/components/converter/profile-summary";
import NewTextConverter from "@/components/converter/new-text-converter";
import { NegativePromptSettings } from "@/components/negative-prompt-settings";
import type { UserProfile } from "@shared/schema";
import { Button } from "@/components/ui/button";
import { ArrowRightLeft, Filter } from "lucide-react";
import { useLocation } from "wouter";

const USER_ID_KEY = "chatToner_userId";
const getUserId = () => {
  let id = localStorage.getItem(USER_ID_KEY);
  if (!id) {
    id = crypto?.randomUUID?.() ?? `user_${Date.now()}`;
    localStorage.setItem(USER_ID_KEY, id);
  }
  return id;
};

export default function ConverterPage() {
  const [, setLoc] = useLocation();
  const userId = getUserId();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [tab, setTab] = useState<"converter" | "settings">("converter"); // ✅ 단일 Tabs 상태

  useEffect(() => {
    const raw = localStorage.getItem("chatToner_profile");
    if (raw) setProfile(JSON.parse(raw));
  }, []);

  if (!profile) {
    return (
      <main className="max-w-4xl mx-auto p-8">
        <p className="mb-4">프로필이 없습니다. 설문을 먼저 진행해 주세요.</p>
        <Button onClick={() => setLoc("/questionnaire")}>설문 시작</Button>
      </main>
    );
  }

  return (
    <main className="max-w-6xl mx-auto p-8">
      <Button
        variant="outline"
        onClick={() => setLoc("/")}
        className="mb-6 bg-white border-gray-200"
      >
        ← 모드 선택으로 돌아가기
      </Button>
      <Button
        variant="destructive"
        className="ml-2"
        onClick={() => {
          localStorage.removeItem("chatToner_profile");
          localStorage.removeItem("chatToner_state");
          localStorage.removeItem("chatToner_userId");
          setLoc("/questionnaire");
        }}
      >
        프로필 초기화
      </Button>

      <Tabs
        value={tab}
        onValueChange={(v) => setTab(v as typeof tab)}
        className="w-full"
      >
        <div className="flex items-center justify-center mb-6">
          <TabsList className="grid w-full max-w-md grid-cols-2">
            <TabsTrigger value="converter" className="flex items-center gap-2">
              <ArrowRightLeft className="h-4 w-4" />
              텍스트 변환
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center gap-2">
              <Filter className="h-4 w-4" />
              필터 설정
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="converter" className="space-y-8">
          <ProfileSummary userProfile={profile} />
          <NewTextConverter userProfile={profile} userId={userId} />
        </TabsContent>

        <TabsContent value="settings" className="space-y-8">
          <NegativePromptSettings
            userId={userId}
            onSave={(preferences) => {
              console.log("네거티브 프롬프트 설정 저장됨:", preferences);
            }}
          />
        </TabsContent>
      </Tabs>
    </main>
  );
}
