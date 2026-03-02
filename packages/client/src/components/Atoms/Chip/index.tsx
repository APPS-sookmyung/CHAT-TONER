import React from "react";
import { cn } from "@/lib/utils";

interface ChipProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  colorScheme?: "yellow" | "purple";
}

export const Chip = ({
  children,
  colorScheme = "yellow",
  className,
  ...props
}: ChipProps) => {
  const baseStyles =
    "px-3 py-1 text-sm font-medium rounded-full inline-block";

  const colorSchemeStyles = {
    yellow: "bg-feature-secondary text-tertiary",
    purple: "bg-feature-primary text-tertiary",
  };

  return (
    <div
      className={cn(baseStyles, colorSchemeStyles[colorScheme], className)}
      {...props}
    >
      {children}
    </div>
  );
};
