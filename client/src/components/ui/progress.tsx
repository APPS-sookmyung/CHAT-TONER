// src/components/ui/progress.tsx
import * as React from "react";
import * as ProgressPrimitive from "@radix-ui/react-progress";
import { cn } from "@/lib/utils";

export interface ProgressProps
  extends React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root> {
  value?: number | null; // 0~100
  variant?: "default" | "primary" | "secondary" | "accent";
  size?: "sm" | "md" | "lg";
}

const Progress = React.forwardRef<
  React.ElementRef<typeof ProgressPrimitive.Root>,
  ProgressProps
>(({ className, value = 0, variant = "default", size = "md", ...props }, ref) => {
  const v = Number.isFinite(Number(value)) ? Number(value) : 0;
  const clampedValue = Math.min(100, Math.max(0, v));

  const variantStyles = {
    default: "bg-blue-500",
    primary: "bg-blue-600",
    secondary: "bg-green-500", 
    accent: "bg-purple-500"
  };

  const sizeStyles = {
    sm: "h-2",
    md: "h-2.5",
    lg: "h-3"
  };

  return (
    <ProgressPrimitive.Root
      ref={ref}
      className={cn(
        "relative w-full overflow-hidden rounded-full bg-gray-100",
        sizeStyles[size],
        className
      )}
      {...props}
    >
      <ProgressPrimitive.Indicator
        className={cn(
          "h-full transition-all duration-300 ease-out",
          variantStyles[variant]
        )}
        style={{ width: `${clampedValue}%` }}
      />
    </ProgressPrimitive.Root>
  );
});
Progress.displayName = "Progress";

export { Progress };
