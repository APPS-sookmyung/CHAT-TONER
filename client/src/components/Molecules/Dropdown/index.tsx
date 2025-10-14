import { useState, useRef, useEffect } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import ChevronDownIcon from "../../../assets/icons/chevron-down.svg?react";
import { cn } from "@/lib/utils";

const dropdownTriggerVariants = cva(
  "text-left rounded-[20px] transition-colors flex items-center justify-between",
  {
    variants: {
      variant: {
        situation: "p-4 bg-white border border-secondary",
        target: "p-4 bg-white border border-secondary",
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
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  const selectedOption = options.find((option) => option.value === value);

  const handleOptionClick = (optionValue: string) => {
    onChange(optionValue);
    setIsOpen(false);
  };

  return (
    <div className="relative w-full" ref={dropdownRef}>
      <button
        type="button"
        className={cn(dropdownTriggerVariants({ variant, size }))}
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-haspopup="listbox"
      >
        <span className={cn({ "text-text-secondary": !selectedOption })}>
          {selectedOption ? selectedOption.label : placeholder}
        </span>
        <ChevronDownIcon
          className={cn(
            "w-4 h-4 ml-2 transition-transform",
            isOpen && "rotate-180"
          )}
        />
      </button>

      {isOpen && (
        <ul
          className="absolute z-10 w-full mt-2 bg-white rounded-[20px] shadow-lg top-full"
          role="listbox"
        >
          {options.map((option) => (
            <li
              key={option.value}
              className="p-3 cursor-pointer hover:bg-gray-100"
              onClick={() => handleOptionClick(option.value)}
              role="option"
              aria-selected={value === option.value}
            >
              {option.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
