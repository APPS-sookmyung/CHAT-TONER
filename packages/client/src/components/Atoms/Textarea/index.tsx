import React from "react";
import { cn } from "@/lib/utils";

interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, readOnly, ...props }, ref) => {
    const baseStyles = [
      "p-4",
      "bg-white rounded-2xl border",
      "text-sm text-text-primary placeholder:text-text-secondary",
      "focus:outline-none focus:ring-1",
      "transition-colors",
    ].join(" ");

    const conditionalStyles = readOnly
      ? "w-full min-h-[200px] border-primary focus:ring-primary/50 cursor-default"
      : "w-full min-h-[150px] border-secondary focus:ring-primary/50 focus:border-primary";

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
