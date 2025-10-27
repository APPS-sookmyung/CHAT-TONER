import { AnalyzeQualityCard } from "@/components/Organisms/AnalyzeQualityCard";

export default function AnalyzeQualityPage() {
  return (
    <div>
      <h1 className="font-bold text-black text-7xl">
        Analyze Quality Page
      </h1>
      <p className="mt-4 mb-12 text-5xl font-medium text-gray-700">
        Analyze document quality instantly
      </p>

      <AnalyzeQualityCard />
    </div>
  );
}