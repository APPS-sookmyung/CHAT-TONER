import React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const cardVariants = cva("p-8 rounded-[30px]", {
  variants: {
    // Variant prop
    variant: {
      primary: "bg-surface",
      secondary: "bg-primary-foreground",
    },
    // Size prop
    size: {
      small: "",
      medium: "",
      large: "",
    },
  },
  compoundVariants: [
    // primary variant
    {
      variant: "primary",
      size: "small",
      className: "w-[574px] h-[334px]",
    },
    {
      variant: "primary",
      size: "medium",
      className: "w-[642px] h-[489px]",
    },
    {
      variant: "primary",
      size: "large",
      className: "w-[559px] h-[615px]",
    },

    // secondary variant
    {
      variant: "secondary",
      size: "small",
      className: "w-[880px] h-[118px]",
    },
    {
      variant: "secondary",
      size: "medium",
      className: "w-[880px] h-[435px]",
    },
  ],

  defaultVariants: {
    variant: "primary",
    size: "medium",
  },
});

// Card variant
export type CardVariantProps = VariantProps<typeof cardVariants>;

interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    CardVariantProps {
  children: React.ReactNode;
}

export const Card = ({
  children,
  className,
  variant,
  size,
  ...props
}: CardProps) => {
  return (
    <div className={cn(cardVariants({ variant, size, className }))} {...props}>
      {children}
    </div>
  );
};
