import { Link } from "wouter";
import { MessageSquare, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import ProfileDropdown from "@/components/profile-dropdown";

export default function Header() {
  const [hasProfile, setHasProfile] = useState(false);
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);

  useEffect(() => {
    const checkProfile = () => {
      try {
        const profile = localStorage.getItem("chatToner_profile");
        setHasProfile(Boolean(profile));
      } catch {
        setHasProfile(false);
      }
    };

    checkProfile();
    // 프로필 변경을 감지하기 위해 storage 이벤트 리스너 추가
    window.addEventListener("storage", checkProfile);

    // 프로필 변경을 더 확실하게 감지하기 위해 interval 추가 (5초마다, 디버깅용)
    const interval = setInterval(checkProfile, 5000);

    return () => {
      window.removeEventListener("storage", checkProfile);
      clearInterval(interval);
    };
  }, []);
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Left: Logo / Title */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-[#00C4B7] rounded-xl flex items-center justify-center">
              <MessageSquare className="text-white w-5 h-5" />
            </div>
            <div>
              <Link href="/" className="text-xl font-bold text-gray-900">
                Chat Toner
              </Link>
              <p className="text-sm text-gray-500">개인 맞춤형 말투 변환기</p>
            </div>
          </div>

          {/* Right: Actions */}
          <div className="flex items-center space-x-4">
            {hasProfile && (
              <Button
                variant="ghost"
                size="icon"
                className="w-8 h-8 rounded-full bg-[#00C4B7] text-white hover:bg-[#00b3a7]"
                onClick={() => setShowProfileDropdown(true)}
              >
                <User className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>
      </div>

      <ProfileDropdown
        open={showProfileDropdown}
        onClose={() => setShowProfileDropdown(false)}
      />
    </header>
  );
}
