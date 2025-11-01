import React from "react";
import { cn } from "@/lib/utils";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, ...props }, ref) => {
    const baseStyles =
      "w-full p-4 bg-white rounded-[20px] border border-secondary focus:outline-none focus:ring-2 focus:ring-primary";

    return <input ref={ref} className={cn(baseStyles, className)} {...props} />;
  }
);

Input.displayName = "Input";
