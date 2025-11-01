import React from "react";
import { cn } from "@/lib/utils";

interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, readOnly, ...props }, ref) => {
    const baseStyles = [
      "p-9",
      "bg-white rounded-[30px] border",
      "text-base text-text-primary placeholder:text-text-secondary",
      "focus:outline-none focus:ring-1",
      "transition-colors",
    ].join(" ");

    const conditionalStyles = readOnly
      ? "w-[554px] h-[346px] border-primary focus:ring-primary/50 cursor-default"
      : "w-[497px] h-90 border-secondary focus:ring-primary/50 focus:border-primary";

    return (
      <textarea
        ref={ref}
        readOnly={readOnly}
        className={cn(baseStyles, conditionalStyles, className)}
        {...props}
      />
    );
  }
);

Textarea.displayName = "Textarea";
