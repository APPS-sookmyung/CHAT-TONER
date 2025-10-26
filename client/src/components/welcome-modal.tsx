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
  onStartUpload: () => void; // Added
}

export default function WelcomeModal({
  open,
  onClose,
  hasProfile,
  onStartQuestionnaire,
  onStartUpload, // Added
}: WelcomeModalProps) {
  if (hasProfile) {
    // Modal for existing users
    return (
      <Dialog open={open} onOpenChange={onClose}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Settings className="w-5 h-5 text-[#00C4B7]" />
              You have a profile!
            </DialogTitle>
            <DialogDescription className="text-base">
              We found your previously configured tone profile.
              <br />
              <span className="text-sm text-gray-500">
                You can edit your profile or use it as is.
              </span>
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col gap-3 mt-4">
            <Button onClick={onStartQuestionnaire} className="w-full">
              Edit Profile (Survey)
            </Button>
            <Button
              variant="outline"
              onClick={onStartUpload}
              className="w-full"
            >
              Edit Profile (Document)
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  // Modal for new users
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <UserPlus className="w-5 h-5 text-[#00C4B7]" />
            Welcome! Create your tone profile
          </DialogTitle>
          <DialogDescription className="pt-2 text-base">
            Create a tone profile that reflects your company's identity. You can choose one of two methods.
          </DialogDescription>
        </DialogHeader>
        <div className="grid grid-cols-1 gap-4 pt-4 md:grid-cols-2">
          <Button
            variant="outline"
            className="flex flex-col items-start justify-start w-full h-auto gap-2 p-4"
            onClick={onStartQuestionnaire}
          >
            <div className="text-lg font-bold">Start with a survey</div>
            <p className="text-sm text-left text-gray-500 whitespace-normal">
              Define your company's tone and manner by answering a few questions.
            </p>
          </Button>
          <Button
            variant="outline"
            className="flex flex-col items-start justify-start w-full h-auto gap-2 p-4"
            onClick={onStartUpload}
          >
            <div className="text-lg font-bold">Start with document upload</div>
            <p className="text-sm text-left text-gray-500 whitespace-normal">
              Upload existing documents and the AI will automatically learn the tone and manner.
            </p>
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
