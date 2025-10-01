import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { User } from "lucide-react";
import { analyzeUserProfile } from "@/lib/prompt-engineering";
import type { UserProfile } from "@shared/schema";

interface ProfileSummaryProps {
  userProfile: UserProfile;
}

export default function ProfileSummary({ userProfile }: ProfileSummaryProps) {
  const analysis = analyzeUserProfile(userProfile);

  const toPct = (v10: number) => v10 * 10; // Convert 10-point scale to 100%

  return (
    <Card className="bg-white border-gray-200">
      <CardContent className="p-6">
        <div className="flex items-center mb-4 space-x-3">
          <div className="flex items-center justify-center w-10 h-10 bg-blue-600 rounded-xl">
            <User className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">당신의 말투 프로필</h3>
            <p className="text-sm text-gray-600">
              수집된 선호도를 기반으로 텍스트를 변환합니다
            </p>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <div className="p-4 border border-gray-100 rounded-lg bg-gray-50">
            <div className="mb-1 text-sm text-gray-600">정중함 정도</div>
            <div className="flex items-center space-x-2">
              <div className="flex-1">
                <Progress
                  value={toPct(userProfile.baseFormalityLevel)}
                  variant="primary"
                  size="sm"
                />
              </div>
              <span className="text-sm font-medium text-gray-700">
                {userProfile.baseFormalityLevel}/10
              </span>
            </div>
          </div>

          <div className="p-4 border border-gray-100 rounded-lg bg-gray-50">
            <div className="mb-1 text-sm text-gray-600">친근함 정도</div>
            <div className="flex items-center space-x-2">
              <div className="flex-1">
                <Progress
                  value={toPct(userProfile.baseFriendlinessLevel)}
                  variant="secondary"
                  size="sm"
                />
              </div>
              <span className="text-sm font-medium text-gray-700">
                {userProfile.baseFriendlinessLevel}/10
              </span>
            </div>
          </div>

          <div className="p-4 border border-gray-100 rounded-lg bg-gray-50">
            <div className="mb-1 text-sm text-gray-600">감정 표현</div>
            <div className="flex items-center space-x-2">
              <div className="flex-1">
                <Progress
                  value={toPct(userProfile.baseEmotionLevel)}
                  variant="accent"
                  size="sm"
                />
              </div>
              <span className="text-sm font-medium text-gray-700">
                {userProfile.baseEmotionLevel}/10
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
