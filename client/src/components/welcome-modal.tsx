import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { UserPlus, Settings } from "lucide-react";

interface WelcomeModalProps {
  open: boolean;
  onClose: () => void;
  hasProfile: boolean;
  onStartQuestionnaire: () => void;
}

export default function WelcomeModal({
  open,
  onClose,
  hasProfile,
  onStartQuestionnaire,
}: WelcomeModalProps) {
  if (hasProfile) {
    // 기존 사용자용 모달
    return (
      <Dialog open={open} onOpenChange={onClose}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Settings className="w-5 h-5 text-[#00C4B7]" />
              프로필이 있으시군요!
            </DialogTitle>
            <DialogDescription className="text-base">
              기존에 설정한 말투 프로필을 발견했습니다.
              <br />
              <span className="text-sm text-gray-500">
                프로필을 수정하거나 그대로 사용하실 수 있습니다.
              </span>
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col gap-3 mt-4">
            <Button onClick={onStartQuestionnaire} className="w-full">
              프로필 수정하기
            </Button>
            <Button variant="outline" onClick={onClose} className="w-full">
              그대로 두기
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  // 신규 사용자용 모달
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <UserPlus className="w-5 h-5 text-[#00C4B7]" />
            아직 프로필이 없네요?
          </DialogTitle>
          <DialogDescription className="text-base">
            더 정확한 말투 변환을 위해 개인 프로필 설정을 권장합니다.
            <br />
            <span className="text-sm text-gray-500">
              5분 정도의 간단한 설문으로 나만의 말투를 정의할 수 있어요.
            </span>
          </DialogDescription>
        </DialogHeader>
        <div className="mt-4">
          <Button onClick={onStartQuestionnaire} className="w-full">
            설문조사 하러 가기
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}