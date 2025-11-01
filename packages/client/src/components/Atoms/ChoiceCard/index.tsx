import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const choiceCardVariants = cva(
  // Base styles
  "p-4 text-center border rounded-lg transition-colors font-medium",
  {
    variants: {
      // 2. isSelected variant
      isSelected: {
        true: "border-primary bg-primary/30",
        false: "border-secondary hover:border-primary bg-white",
      },
      // 3. size variant
      size: {
        sm: "w-[215px]",
        lg: "w-[333px]",
      },
    },
    defaultVariants: {
      isSelected: false,
      size: "sm",
    },
  }
);

interface ChoiceCardProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof choiceCardVariants> {
  children: React.ReactNode;
}

export const ChoiceCard = ({
  children,
  className,
  isSelected,
  size,
  ...props
}: ChoiceCardProps) => {
  return (
    <button
      className={cn(choiceCardVariants({ isSelected, size, className }))}
      {...props}
    >
      {children}
    </button>
  );
};
