import { ChipGroup } from "@/components/Molecules/Chipgroup";
import { Link } from "react-router-dom";

const ChoicePage = () => {
  // Data for the first ChipGroup
  const styleChips = [
    { label: "directness", colorScheme: "yellow" as const },
    { label: "softness", colorScheme: "yellow" as const },
    { label: "politeness", colorScheme: "yellow" as const },
    { label: "clarity", colorScheme: "yellow" as const },
    { label: "consistency", colorScheme: "yellow" as const },
    { label: "formality", colorScheme: "yellow" as const },
    { label: "conciseness", colorScheme: "yellow" as const },
    { label: "empathy", colorScheme: "yellow" as const },
  ];

  // Data for the second ChipGroup
  const qualityChips = [
    { label: "compliance", colorScheme: "purple" as const },
    { label: "grammar", colorScheme: "purple" as const },
    { label: "formality", colorScheme: "purple" as const },
    { label: "accuracy", colorScheme: "purple" as const },
    { label: "readability", colorScheme: "purple" as const },
    { label: "consistency", colorScheme: "purple" as const },
    { label: "clarity", colorScheme: "purple" as const },
    { label: "protocol", colorScheme: "purple" as const },
    { label: "professionalism", colorScheme: "purple" as const },
  ];

  return (
    <div className="flex items-center justify-center min-h-screen pt-24">
      <div className="flex flex-row items-center gap-20">
        <div className="pt-4">
          <h1 className="items-center font-bold leading-tight text-black text-7xl">
            Use Chat Toner <br />
            for your <span className="text-primary">workflow</span>
          </h1>
        </div>
        <div className="flex flex-col gap-8">
          <Link
            to="/transform-style"
            className="block transition-transform duration-200 ease-in-out hover:scale-105"
          >
            <ChipGroup
              title="Transform Style"
              chips={styleChips}
              variant="primary"
              size="small"
            />
          </Link>
          <Link
            to="/analyze-quality"
            className="block transition-transform duration-200 ease-in-out hover:scale-105"
          >
            <ChipGroup
              title="Analyze Quality"
              chips={qualityChips}
              variant="primary"
              size="small"
            />
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ChoicePage;
