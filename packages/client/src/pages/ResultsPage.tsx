import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PATH } from "@/constants/paths";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle, Download, Sparkles, User } from "lucide-react";

// Company profile interface matching backend response
interface CompanyProfile {
  id: number;
  userId: string;
  companyProfile: string;
  companyContext: {
    companySize: string;
    teamSize: string;
    primaryFunction: string;
    communicationStyle: string;
    primaryChannel: string;
    primaryAudience: string[];
    sizeCharacteristics: string[];
    functionCharacteristics: string[];
  };
  surveyResponses: Record<string, any>;
  createdAt: string;
  message?: string;
  profileType: string;
}

export default function ResultsPage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<CompanyProfile | null>(null);

  useEffect(() => {
    const raw = localStorage.getItem("chatToner_profile");
    if (raw) {
      setProfile(JSON.parse(raw));
    } else {
      console.warn("No company profile found in localStorage");
    }
  }, []);

  if (!profile) {
    return <div className="p-8 text-center">Loading profile...</div>;
  }

  return (
    <main className="max-w-6xl p-8 mx-auto">
      <Card className="shadow-sm border border-gray-200">
        <CardContent className="p-8 text-center">
          <div className="mb-6">
            <div className="w-16 h-16 bg-success/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="text-success w-8 h-8" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Company Profile Created!</h2>
            <p className="text-gray-600">Your team communication guide has been successfully generated.</p>
          </div>

          <div className="bg-gray-50 rounded-xl p-6 mb-6">
            <h3 className="font-semibold text-gray-900 mb-4">Summary of Your Team Profile</h3>
            <div className="grid md:grid-cols-2 gap-4 text-left">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Company Size:</span>
                <span className="font-medium">{profile.companyContext?.companySize || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Team Size:</span>
                <span className="font-medium">{profile.companyContext?.teamSize || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Primary Function:</span>
                <span className="font-medium capitalize">{profile.companyContext?.primaryFunction || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Communication Style:</span>
                <span className="font-medium capitalize">{profile.companyContext?.communicationStyle || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Primary Channel:</span>
                <span className="font-medium capitalize">{profile.companyContext?.primaryChannel || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Profile Type:</span>
                <span className="font-medium">{profile.profileType || 'Company-based'}</span>
              </div>
            </div>

            {profile.message && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-700">{profile.message}</p>
              </div>
            )}
          </div>

          <div className="flex justify-center space-x-4">
            <Button
              variant="outline"
              onClick={() => {
                const dataStr = JSON.stringify(profile, null, 2);
                const url = URL.createObjectURL(
                  new Blob([dataStr], { type: "application/json" })
                );
                const a = document.createElement("a");
                a.href = url;
                a.download = "company-communication-profile.json";
                a.click();
              }}
              className="flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Export Data</span>
            </Button>
            <Button
              variant="outline"
              onClick={() => navigate(PATH.PROFILE)}
              className="flex items-center space-x-2"
            >
              <User className="w-4 h-4" />
              <span>View Full Profile</span>
            </Button>
            <Button
              onClick={() => navigate(PATH.CHOICE)}
              className="flex items-center space-x-2 px-8"
            >
              <Sparkles className="w-4 h-4" />
              <span>Start Using Guide</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </main>
  );
}
