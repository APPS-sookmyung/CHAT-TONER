import { useState, useEffect } from 'react';
import { useLocation } from 'wouter';
import type { UserProfile } from '@shared/schema';
import ProfileSummary from '@/components/converter/profile-summary';
import StyleConverter from '@/components/converter/style-converter';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Terminal } from 'lucide-react';

export default function ConverterPage() {
  const [, setLocation] = useLocation();
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    try {
      const profileString = localStorage.getItem("chatToner_profile");
      if (profileString) {
        setUserProfile(JSON.parse(profileString));
      }
    } catch (error) {
      console.error("Failed to load user profile:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  if (isLoading) {
    return <div className="text-center p-8">Loading profile...</div>;
  }

  if (!userProfile) {
    return (
        <div className="max-w-2xl mx-auto mt-16 text-center">
            <Alert>
                <Terminal className="h-4 w-4" />
                <AlertTitle>프로필을 찾을 수 없습니다!</AlertTitle>
                <AlertDescription>
                    <p>스타일 변환기를 사용하려면, 먼저 나만의 말투 프로필을 정의해야 합니다.</p>
                    <Button onClick={() => setLocation('/style-definition')} className="mt-4">
                        스타일 정의하러 가기
                    </Button>
                </AlertDescription>
            </Alert>
        </div>
    );
  }

  return (
    <div className="space-y-8">
      <ProfileSummary userProfile={userProfile} />
      <StyleConverter userProfile={userProfile} />
    </div>
  );
}
