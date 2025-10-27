import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Profile from "@/assets/icons/profile.svg?react";
import ProfileDropdown from "@/components/Organisms/ProfileDropdown";
import type { UserProfile } from "@shared/schema";
import { PATH } from "@/constants/paths";

export const Header = () => {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null); // Add userProfile state

  useEffect(() => {
    const profileString = localStorage.getItem("chatToner_profile");
    if (profileString) {
      setUserProfile(JSON.parse(profileString));
    }
  }, []);

  const handleHomeClick = () => {
    navigate(PATH.HOME);
  };

  const handleProfileClick = () => {
    setIsModalOpen(!isModalOpen);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };
  return (
    <div className="flex justify-between px-[50px] py-[30px]">
      <button
        className="justify-start text-3xl font-medium text-black cursor-pointer"
        onClick={handleHomeClick}
      >
        Chat Toner
      </button>

      <div className="relative justify-end">
        <button
          type="button"
          className="justify-end cursor-pointer w-9 h-9"
          onClick={handleProfileClick}
          aria-haspopup="true"
          aria-expanded={isModalOpen}
        >
          <Profile />
        </button>

        <ProfileDropdown
          open={isModalOpen}
          onClose={handleCloseModal}
          userProfile={userProfile}
        />
      </div>
    </div>
  );
};
