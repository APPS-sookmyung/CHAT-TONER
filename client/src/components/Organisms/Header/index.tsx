import { useState } from "react";
import Profile from "@/assets/icons/profile.svg?react";
import ProfileDropdown from "@/components/Organisms/ProfileDropdown";

export const Header = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleHomeClick = () => {
    window.location.href = "/";
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

        {/* 4. isModalOpen이 true일 때만 모달 렌더링 */}
        <ProfileDropdown open={isModalOpen} onClose={handleCloseModal} />
      </div>
    </div>
  );
};
