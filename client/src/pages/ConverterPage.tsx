import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import type { UserProfile } from '@shared/schema';
import ProfileSummary from '@/components/converter/profile-summary';
import StyleConverter from '@/components/converter/style-converter';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Terminal } from 'lucide-react';

export default function ConverterPage() {
  const navigate = useNavigate();
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
                <AlertTitle>Profile not found!</AlertTitle>
                <AlertDescription>
                    <p>To use the style converter, you must first define your own tone profile.</p>
                    <Button onClick={() => navigate('/style-definition')} className="mt-4">
                        Go to Style Definition
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
