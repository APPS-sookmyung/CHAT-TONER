import { useState, useEffect } from "react";
import { User, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { useLocation } from "wouter";
import type { UserProfile } from "@shared/schema";

interface ProfileDropdownProps {
  open: boolean;
  onClose: () => void;
}

export default function ProfileDropdown({
  open,
  onClose,
}: ProfileDropdownProps) {
  const [, setLocation] = useLocation();
  const [profile, setProfile] = useState<UserProfile | null>(null);

  useEffect(() => {
    if (open) {
      try {
        const profileData = localStorage.getItem("chatToner_profile");
        if (profileData) {
          setProfile(JSON.parse(profileData));
        }
      } catch {
        setProfile(null);
      }
    }
  }, [open]);

  if (!open || !profile) return null;

  const handleEditProfile = () => {
    onClose();
    setLocation("/style-definition");
  };

  const formatDate = (date: string | Date) => {
    try {
      return new Date(date).toLocaleDateString("ko-KR");
    } catch {
      return "날짜 정보 없음";
    }
  };

  return (
    <div className="fixed inset-0 z-50" onClick={onClose}>
      <div
        className="absolute top-20 right-8 bg-white rounded-lg shadow-lg border p-6 w-80"
        onClick={(e) => e.stopPropagation()}
      >
        {/* 헤더 */}
        <div className="flex items-center gap-3 mb-4 pb-3 border-b">
          <div className="w-10 h-10 rounded-full bg-[#00C4B7] text-white flex items-center justify-center">
            <User className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">내 프로필</h3>
            <p className="text-sm text-gray-500">
              {profile.completedAt
                ? formatDate(profile.completedAt)
                : "완료일 정보 없음"}
            </p>
          </div>
        </div>

        {/* 스타일 지표 */}
        <div className="space-y-4 mb-6">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">정중함</span>
              <span className="text-sm text-gray-500">
                {profile.baseFormalityLevel}/10
              </span>
            </div>
            <Progress value={profile.baseFormalityLevel * 10} className="h-2" />
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">친근함</span>
              <span className="text-sm text-gray-500">
                {profile.baseFriendlinessLevel}/10
              </span>
            </div>
            <Progress
              value={profile.baseFriendlinessLevel * 10}
              className="h-2"
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">
                감정 표현
              </span>
              <span className="text-sm text-gray-500">
                {profile.baseEmotionLevel}/10
              </span>
            </div>
            <Progress value={profile.baseEmotionLevel * 10} className="h-2" />
          </div>
        </div>

        {/* 액션 버튼 */}
        <div className="flex flex-col gap-2">
          <Button
            onClick={handleEditProfile}
            className="w-full flex items-center gap-2"
          >
            <Settings className="w-4 h-4" />
            프로필 수정하기
          </Button>
          <Button variant="outline" onClick={onClose} className="w-full">
            닫기
          </Button>
        </div>
      </div>
    </div>
  );
}
