import { cn } from "@/lib/utils";

interface Option {
  label: string;
  value: string;
}

interface SegmentedControlProps {
  options: Option[];
  value?: string;
  onChange: (value: string) => void;
  className?: string;
}

export const SegmentedControl = ({
  options,
  value,
  onChange,
  className,
}: SegmentedControlProps) => {
  const containerStyles = "flex w-full bg-surface rounded-full";

  return (
    <div className={cn(containerStyles, className)}>
      {options.map((option) => (
        <button
          key={option.value}
          onClick={() => onChange(option.value)}
          className={cn(
            "w-full rounded-full py-5 px-4 text-center font-medium transition-all duration-300",
            value === option.value
              ? "bg-black text-white"
              : "bg-transparent text-black hover:bg-gray-200"
          )}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
};
