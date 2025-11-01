// src/components/converter/profile-summary.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { UserProfile as BaseUserProfile } from "@shared/schema";

type Profile = BaseUserProfile & {
  // Session values may or may not exist, so make them optional
  sessionFormalityLevel?: number | string;
  sessionFriendlinessLevel?: number | string;
  sessionEmotionLevel?: number | string; // ← Emotional(X), Emotion(O)
  sessionDirectnessLevel?: number | string;
};

function toNum10(x: unknown, fallback = 5) {
  // Safe conversion as it might come as string + clamp
  const n = Number(x);
  if (Number.isFinite(n)) return Math.min(10, Math.max(0, n));
  return fallback;
}
const toPct = (v10: number) => v10 * 10; // Convert 10-point scale to 100%

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
        <CardTitle>Your Tone Profile</CardTitle>
        <p className="text-sm text-muted-foreground">
          Converts text based on your collected preferences
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <div className="flex items-center justify-between text-sm mb-1">
            <span>Formality Level</span>
            <span>{formality}/10</span>
          </div>
          <Progress value={toPct(formality)} className="h-2" />
        </div>

        <div>
          <div className="flex items-center justify-between text-sm mb-1">
            <span>Friendliness Level</span>
            <span>{friendliness}/10</span>
          </div>
          <Progress value={toPct(friendliness)} className="h-2" />
        </div>

        <div>
          <div className="flex items-center justify-between text-sm mb-1">
            <span>Emotion Expression</span>
            <span>{emotion}/10</span>
          </div>
          <Progress value={toPct(emotion)} className="h-2" />
        </div>

        <div>
          <div className="flex items-center justify-between text-sm mb-1">
            <span>Directness</span>
            <span>{directness}/10</span>
          </div>
          <Progress value={toPct(directness)} className="h-2" />
        </div>
      </CardContent>
    </Card>
  );
}
