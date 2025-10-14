import { cn } from "@/lib/utils";

interface ProgressBarProps {
  label: string;
  currentStep: number;
  totalSteps: number;
  className?: string;
}

export const ProgressBar = ({
  label,
  currentStep,
  totalSteps,
  className,
}: ProgressBarProps) => {
  const percent = (currentStep / totalSteps) * 100;

  return (
    <div className={cn("w-full", className)}>
      <div className="flex items-center gap-[400px] mb-3">
        <span className="text-3xl font-semibold text-text-primary">
          {label}
        </span>
        <span className="font-semibold">
          <span className="text-3xl text-primary">{currentStep}</span>
          <span className="text-3xl text-text-primary">/{totalSteps}</span>
        </span>
      </div>
      <div className="w-[711px] bg-secondary rounded-full h-2.5">
        <div
          className="bg-primary h-2.5 rounded-full transition-all duration-500"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
};
