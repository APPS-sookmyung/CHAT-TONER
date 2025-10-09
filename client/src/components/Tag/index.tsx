import React from "react";
import { cn } from "@/lib/utils";

interface TagProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  variant?: "chip";
  colorScheme?: "yellow" | "purple";
}

export const Tag = ({
  children,
  variant = "chip",
  colorScheme = "yellow",
  className,
  ...props
}: TagProps) => {
  const baseStyles =
    "px-[19px] py-[6px] text-2xl font-medium rounded-[30px] inline-block";

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
