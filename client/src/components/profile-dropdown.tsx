import { useState } from "react";
import { Building, CheckCircle, Info, Plus, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";

interface CompanyProfile {
  company_name?: string;
  communication_style?: string;
  ready_for_analysis?: boolean;
  guidelines_count?: number;
  negative_prompts?: string[];
}

const MOCK_COMPANY_PROFILE: CompanyProfile = {
  company_name: "(주)챗토너 컴퍼니",
  communication_style: "간결하고 명확함",
  ready_for_analysis: true,
  guidelines_count: 5,
  negative_prompts: [
    "'수고하세요' 대신 '감사합니다' 사용",
    "지나치게 긴 서론 지양",
  ],
};

interface ProfileDropdownProps {
  open: boolean;
  onClose: () => void;
}

export default function ProfileDropdown({
  open,
  onClose,
}: ProfileDropdownProps) {
  const { toast } = useToast();
  const [profile, setProfile] = useState<CompanyProfile>(MOCK_COMPANY_PROFILE);
  const [newPrompt, setNewPrompt] = useState("");
  const [isComposing, setIsComposing] = useState(false);

  const handleAddPrompt = () => {
    if (newPrompt && !profile.negative_prompts?.includes(newPrompt)) {
      const updatedPrompts = [...(profile.negative_prompts || []), newPrompt];
      setProfile({ ...profile, negative_prompts: updatedPrompts });
      setNewPrompt("");
      toast({
        title: "성공",
        description: "'이렇게 쓰지 않기' 규칙이 추가되었습니다.",
      });
    } else {
      toast({
        variant: "destructive",
        title: "오류",
        description: "이미 추가된 내용이거나, 입력값이 없습니다.",
      });
    }
  };

  const handleRemovePrompt = (promptToRemove: string) => {
    const updatedPrompts = profile.negative_prompts?.filter(
      (p) => p !== promptToRemove
    );
    setProfile({ ...profile, negative_prompts: updatedPrompts });
    toast({ title: "성공", description: "규칙이 삭제되었습니다." });
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50" onClick={onClose}>
      <div
        className="absolute top-20 right-8 bg-white rounded-lg shadow-lg border p-6 w-96 max-h-[80vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-3 pb-4 mb-4 border-b">
          <div className="flex items-center justify-center w-10 h-10 text-white bg-blue-600 rounded-lg">
            <Building className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">
              {profile.company_name || "회사 프로필"}
            </h3>
            <p className="text-sm text-gray-500">AI 프로필 관리</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-6">
          <InfoCard
            icon={<Info className="w-5 h-5 text-gray-500" />}
            label="소통 스타일"
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
            label="프로필 상태"
            value={profile.ready_for_analysis ? "준비 완료" : "설정 필요"}
          />
        </div>

        <div className="mb-6 space-y-4">
          <h4 className="text-sm font-medium text-gray-800">
            이렇게 쓰지 않기 (Negative Prompts)
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
              placeholder="예: '수고하세요' 사용 금지"
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

        <Button variant="outline" onClick={onClose} className="w-full">
          닫기
        </Button>
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
