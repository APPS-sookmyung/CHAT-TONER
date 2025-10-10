import { useState } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import ChevronDownIcon from "../../../assets/icons/chevron-down.svg?react";
import { cn } from "@/lib/utils";

const dropdownTriggerVariants = cva(
  "text-left rounded-lg transition-colors flex items-center justify-between",
  {
    variants: {
      variant: {
        situation: "p-4 bg-white",
        target: "p-4 bg-white",
      },
      size: {
        default: "w-[299px] h-[63px]",
        compact: "w-[164px] h-[63px]",
      },
    },
    defaultVariants: {
      variant: "situation",
      size: "default",
    },
  }
);

interface Option {
  label: string;
  value: string;
}

interface DropdownProps extends VariantProps<typeof dropdownTriggerVariants> {
  options: Option[];
  value?: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export const Dropdown = ({
  options,
  value,
  onChange,
  placeholder = "Select an option",
  variant,
  size,
}: DropdownProps) => {
  const [isOpen, setIsOpen] = useState(false);

  const selectedOption = options.find((option) => option.value === value);

  const handleOptionClick = (optionValue: string) => {
    onChange(optionValue);
    setIsOpen(false);
  };

  return (
    <div className="relative w-full">
      <button
        type="button"
        className={cn(dropdownTriggerVariants({ variant, size }))}
        onClick={() => setIsOpen(!isOpen)}
      >
        <span>{selectedOption ? selectedOption.label : placeholder}</span>
        <ChevronDownIcon
          className={`w-4 h-4 ml-2 transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </button>

      {isOpen && (
        <ul className="absolute z-10 w-full mt-2 bg-white rounded-lg shadow-lg top-full">
          {options.map((option) => (
            <li
              key={option.value}
              className="p-3 cursor-pointer hover:bg-gray-100"
              onClick={() => handleOptionClick(option.value)}
            >
              {option.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
