import React from "react";
import { cn } from "@/lib/utils";

type ButtonVariant = "primary" | "secondary";
type ButtonSize = "sm" | "md" | "lg" | "xl";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
}

const buttonVariants = {
  primary: "bg-primary text-primary-foreground hover:bg-primary/90",
  secondary: "bg-secondary text-text-primary hover:bg-secondary/80",
} as const;

const buttonSizes = {
  sm: "h-9 px-4 text-xs font-medium",
  md: "h-12 px-6 py-2 text-base font-medium",
  lg: "h-14 px-8 py-3 text-lg font-bold",
  xl: "h-16 px-12 py-4 text-xl font-bold",
} as const;

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    { children, variant = "primary", size = "md", className, ...props },
    ref
  ) => {
    const baseStyles =
      "inline-flex items-center justify-center font-bold rounded-lg transition-colors text-center";

    const classes = cn(
      baseStyles,
      buttonVariants[variant],
      buttonSizes[size],
      className
    );

    return (
      <button ref={ref} className={classes} {...props}>
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
export default Button;
