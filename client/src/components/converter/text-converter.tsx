// src/components/converter/profile-summary.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { UserProfile as BaseUserProfile } from "@shared/schema";

type Profile = BaseUserProfile & {
  // 세션 값은 있을 수도/없을 수도 있으니 옵션으로
  sessionFormalityLevel?: number | string;
  sessionFriendlinessLevel?: number | string;
  sessionEmotionLevel?: number | string; // ← Emotional(X), Emotion(O)
  sessionDirectnessLevel?: number | string;
};

function toNum10(x: unknown, fallback = 5) {
  // 문자열로 올 수도 있으니 안전 변환 + 클램프
  const n = Number(x);
  if (Number.isFinite(n)) return Math.min(10, Math.max(0, n));
  return fallback;
}
const toPct = (v10: number) => v10 * 10; // 10점 만점을 100%로

export default function ProfileSummary({
  userProfile,
}: {
  userProfile: Profile;
}) {
  const formality = toNum10(
    userProfile.sessionFormalityLevel ?? userProfile.baseFormalityLevel
  );
  const friendliness = toNum10(
    userProfile.sessionFriendlinessLevel ?? userProfile.baseFriendlinessLevel
  );
  const emotion = toNum10(
    userProfile.sessionEmotionLevel ?? userProfile.baseEmotionLevel
  );
  const directness = toNum10(
    userProfile.sessionDirectnessLevel ?? userProfile.baseDirectnessLevel
  );

  return (
    <Card className="shadow-sm border border-gray-200">
      <CardHeader>
        <CardTitle>당신의 말투 프로필</CardTitle>
        <p className="text-sm text-muted-foreground">
          수집된 선호도를 기반으로 텍스트를 변환합니다
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <div className="flex items-center justify-between text-sm mb-1">
            <span>정중함 정도</span>
            <span>{formality}/10</span>
          </div>
          <Progress value={toPct(formality)} className="h-2" />
        </div>

        <div>
          <div className="flex items-center justify-between text-sm mb-1">
            <span>친근함 정도</span>
            <span>{friendliness}/10</span>
          </div>
          <Progress value={toPct(friendliness)} className="h-2" />
        </div>

        <div>
          <div className="flex items-center justify-between text-sm mb-1">
            <span>감정 표현</span>
            <span>{emotion}/10</span>
          </div>
          <Progress value={toPct(emotion)} className="h-2" />
        </div>

        <div>
          <div className="flex items-center justify-between text-sm mb-1">
            <span>직설성</span>
            <span>{directness}/10</span>
          </div>
          <Progress value={toPct(directness)} className="h-2" />
        </div>
      </CardContent>
    </Card>
  );
}
