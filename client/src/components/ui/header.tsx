import { Link } from "wouter";
import { MessageSquare, Settings, ArrowRightLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

type HeaderProps = {
  /** 설문↔변환 토글 버튼을 보여줄지 여부 (userProfile 있을 때만 true로) */
  showPhaseToggle?: boolean;
  /** 토글 버튼 텍스트: "변환기로 이동" | "설문으로 이동" */
  phaseToggleText?: string;
  /** 토글 버튼 클릭 핸들러 */
  onPhaseToggle?: () => void;
  /** 우측에 추가로 넣을 요소 (선택) */
  rightExtra?: React.ReactNode;
};

export default function Header({
  showPhaseToggle = true,
  phaseToggleText = "",
  onPhaseToggle,
  rightExtra,
}: HeaderProps) {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Left: Logo / Title */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center">
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
            {showPhaseToggle && (
              <Button
                variant="outline"
                size="sm"
                onClick={onPhaseToggle}
                className="flex md:flex items-center space-x-2"
              >
                <ArrowRightLeft className="w-4 h-4" />
                <span>{phaseToggleText}</span>
              </Button>
            )}
            {rightExtra}
          </div>
        </div>
      </div>
    </header>
  );
}
