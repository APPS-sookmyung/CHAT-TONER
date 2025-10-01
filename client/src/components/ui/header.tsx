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
    // Add storage event listener to detect profile changes
    window.addEventListener("storage", checkProfile);

    // Add interval for more reliable profile change detection (every 5 seconds, for debugging)
    const interval = setInterval(checkProfile, 5000);

    return () => {
      window.removeEventListener("storage", checkProfile);
      clearInterval(interval);
    };
  }, []);
  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-6xl px-4 mx-auto sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left: Logo / Title */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-[#00C4B7] rounded-xl flex items-center justify-center">
              <MessageSquare className="w-5 h-5 text-white" />
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
