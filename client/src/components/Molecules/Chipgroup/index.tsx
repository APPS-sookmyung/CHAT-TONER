import { Card, type CardVariantProps } from "@/components/Molecules/Card";
import { Chip } from "@/components/Atoms/Chip";
import { cn } from "@/lib/utils";

interface ChipgroupProps extends CardVariantProps {
  title: string;
  chips: { label: string; colorScheme: "yellow" | "purple" }[];
  className?: string;
}

export const ChipGroup = ({
  title,
  chips,
  variant,
  size,
  className,
}: ChipgroupProps) => {
  return (
    <Card
      variant={variant}
      size={size}
      className={cn("flex flex-col justify-center", className)}
    >
      <div>
        <h2 className="mb-10 text-5xl font-bold">{title}</h2>
        <div className="flex flex-wrap gap-2.25">
          {chips.map((chip) => (
            <Chip key={chip.label} colorScheme={chip.colorScheme}>
              {chip.label}
            </Chip>
          ))}
        </div>
      </div>
    </Card>
  );
};
