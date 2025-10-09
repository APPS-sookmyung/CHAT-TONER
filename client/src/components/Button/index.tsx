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
  sm: "w-36 h-14 px-8 py-3.5 text-xl font-medium",
  md: "w-80 h-32 px-20 py-5 text-[1.75rem] leading-10 font-medium",
  lg: "w-72 h-20 px-9 py-5.5 text-4xl font-bold",
  xl: "w-[31.06rem] h-20 px-36 py-3 text-[2.50rem] font-bold",
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
