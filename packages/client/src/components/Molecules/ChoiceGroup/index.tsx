import { ChoiceCard } from "@/components/Atoms/ChoiceCard";
import { cn } from "@/lib/utils";

interface Option {
  label: string;
  value: string;
}

interface ChoiceGroupProps {
  options: Option[];
  value?: string;
  onChange: (value: string) => void;
  size?: "sm" | "lg";
  className?: string;
}

export const ChoiceGroup = ({
  options,
  value,
  onChange,
  size = "sm",
  className,
}: ChoiceGroupProps) => {
  const layoutStyles = {
    sm: "grid-cols-3 gap-x-[39px]",
    lg: "grid-cols-2 gap-x-[48px]",
  };

  return (
    <div className={cn("grid gap-y-[19px]", layoutStyles[size], className)}>
      {options.map((option) => (
        <ChoiceCard
          key={option.value}
          size={size}
          isSelected={value === option.value}
          onClick={() => onChange(option.value)}
        >
          {option.label}
        </ChoiceCard>
      ))}
    </div>
  );
};
