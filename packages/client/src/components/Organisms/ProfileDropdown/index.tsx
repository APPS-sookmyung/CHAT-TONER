import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Building, CheckCircle, Info, Plus, X, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { PATH } from "@/constants/paths";
import type { UserProfile } from "@shared/schema";

interface CompanyProfile {
  company_name?: string;
  communication_style?: string;
  ready_for_analysis?: boolean;
  guidelines_count?: number;
  negative_prompts?: string[];
}

// Default profile if no userProfile is provided
const MOCK_COMPANY_PROFILE_DEFAULT: CompanyProfile = {
  company_name: "Guest Company",
  communication_style: "Default Style",
  ready_for_analysis: false,
  guidelines_count: 0,
  negative_prompts: [],
};

interface ProfileDropdownProps {
  open: boolean;
  onClose: () => void;
  userProfile: UserProfile | null;
}

export default function ProfileDropdown({
  open,
  onClose,
  userProfile,
}: ProfileDropdownProps) {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [profile, setProfile] = useState<CompanyProfile>(() => {
    if (userProfile) {
      return {
        company_name: userProfile.company_name || "N/A",
        communication_style: userProfile.communication_style || "N/A",
        ready_for_analysis: !!userProfile.completedAt,
        negative_prompts: [], // Initialize empty, will be managed internally
        guidelines_count: 0, // Initialize 0, will be managed internally
      };
    }
    return MOCK_COMPANY_PROFILE_DEFAULT;
  });
  const [newPrompt, setNewPrompt] = useState("");
  const [isComposing, setIsComposing] = useState(false);

  // Update internal profile state when userProfile prop changes
  useEffect(() => {
    if (userProfile) {
      setProfile((prevProfile) => ({
        ...prevProfile,
        company_name: userProfile.company_name || "N/A",
        communication_style: userProfile.communication_style || "N/A",
        ready_for_analysis: !!userProfile.completedAt,
      }));
    }
  }, [userProfile]); // Depend on userProfile prop

  const handleAddPrompt = () => {
    if (newPrompt && !profile.negative_prompts?.includes(newPrompt)) {
      const updatedPrompts = [...(profile.negative_prompts || []), newPrompt];
      setProfile({ ...profile, negative_prompts: updatedPrompts });
      setNewPrompt("");
      toast({
        title: "Success",
        description: "The 'Don't write like this' rule has been added.",
      });
    } else {
      toast({
        variant: "destructive",
        title: "Error",
        description:
          "This content has already been added, or there is no input.",
      });
    }
  };

  const handleRemovePrompt = (promptToRemove: string) => {
    const updatedPrompts = profile.negative_prompts?.filter(
      (p) => p !== promptToRemove
    );
    setProfile({ ...profile, negative_prompts: updatedPrompts });
    toast({ title: "Success", description: "The rule has been deleted." });
  };

  const handleViewProfile = () => {
    navigate(PATH.PROFILE);
    onClose();
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50" onClick={onClose}>
      <div
        className="absolute top-22 right-14 bg-white rounded-lg shadow-lg border-secondary p-6 w-96 max-h-[80vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <Button
          variant="ghost"
          size="icon"
          className="absolute w-8 h-8 text-gray-500 top-4 right-4 hover:bg-gray-100"
          onClick={onClose}
        >
          <X className="w-5 h-5 cursor-pointer" />
        </Button>
        <div className="flex items-center gap-3 pb-4 mb-4 border-b-secondary">
          <div className="flex items-center justify-center w-10 h-10 text-white rounded-lg bg-primary">
            <Building className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">
              {profile.company_name || "Company Profile"}
            </h3>
            <p className="text-sm text-gray-500">AI Profile Management</p>
          </div>
        </div>

        <div className="mb-4">
          <Button
            onClick={handleViewProfile}
            className="w-full flex items-center gap-2"
            variant="outline"
          >
            <User className="w-4 h-4" />
            내 커뮤니케이션 프로필 보기
          </Button>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-6">
          <InfoCard
            icon={<Info className="w-5 h-5 text-gray-500" />}
            label="Communication Style"
            value={profile.communication_style || "-"}
          />
          <InfoCard
            icon={
              <CheckCircle
                className={`w-5 h-5 ${
                  profile.ready_for_analysis
                    ? "text-green-500"
                    : "text-yellow-500"
                }`}
              />
            }
            label="Profile Status"
            value={profile.ready_for_analysis ? "Ready" : "Setup required"}
          />
        </div>

        <div className="mb-6 space-y-4">
          <h4 className="text-sm font-medium text-gray-800">
            Don't write like this (Negative Prompts)
          </h4>
          <div className="space-y-2">
            {profile.negative_prompts?.map((prompt, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 rounded-md bg-gray-50"
              >
                <p className="text-sm text-gray-700">{prompt}</p>
                <Button
                  variant="ghost"
                  size="icon"
                  className="w-6 h-6"
                  onClick={() => handleRemovePrompt(prompt)}
                >
                  <X className="w-4 h-4 text-gray-500" />
                </Button>
              </div>
            ))}
          </div>
          <div className="flex gap-2">
            <Input
              placeholder="e.g., Do not use 'Keep up the good work'"
              value={newPrompt}
              onCompositionStart={() => setIsComposing(true)}
              onCompositionEnd={() => setIsComposing(false)}
              onChange={(e) => setNewPrompt(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !isComposing) {
                  handleAddPrompt();
                }
              }}
            />
            <Button onClick={handleAddPrompt}>
              <Plus className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

function InfoCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="p-3 border border-gray-100 rounded-lg bg-gray-50">
      <div className="flex items-center gap-3">
        {icon}
        <div>
          <div className="text-xs text-gray-500">{label}</div>
          <div className="text-sm font-semibold text-gray-800">{value}</div>
        </div>
      </div>
    </div>
  );
}
