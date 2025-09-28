import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { UserPlus, Settings, FileUp } from "lucide-react";

interface WelcomeModalProps {
  open: boolean;
  onClose: () => void;
  hasProfile: boolean;
  onStartQuestionnaire: () => void;
  onStartUpload: () => void; // 추가
}

export default function WelcomeModal({
  open,
  onClose,
  hasProfile,
  onStartQuestionnaire,
  onStartUpload, // 추가
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
              프로필 수정하기 (설문)
            </Button>
            <Button variant="outline" onClick={onStartUpload} className="w-full">
              프로필 수정하기 (문서)
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  // 신규 사용자용 모달
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <UserPlus className="w-5 h-5 text-[#00C4B7]" />
            환영합니다! 말투 프로필 만들기
          </DialogTitle>
          <DialogDescription className="text-base pt-2">
            기업의 정체성을 담은 말투 프로필을 만들어 보세요. 두 가지 방법 중
            하나를 선택할 수 있습니다.
          </DialogDescription>
        </DialogHeader>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4">
          <Button
            variant="outline"
            className="h-auto w-full p-4 flex flex-col items-start justify-start gap-2"
            onClick={onStartQuestionnaire}
          >
            <div className="font-bold text-lg">설문조사로 시작</div>
            <p className="text-sm text-left text-gray-500 whitespace-normal">
              몇 가지 질문에 답변하여 기업의 톤앤매너를 정의합니다.
            </p>
          </Button>
          <Button
            variant="outline"
            className="h-auto w-full p-4 flex flex-col items-start justify-start gap-2"
            onClick={onStartUpload}
          >
            <div className="font-bold text-lg">문서 업로드로 시작</div>
            <p className="text-sm text-left text-gray-500 whitespace-normal">
              기존 문서를 업로드하여 AI가 톤앤매너를 자동으로 학습합니다.
            </p>
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
