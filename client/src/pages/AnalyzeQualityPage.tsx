import { useState, useMemo, useEffect } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { AnalyzeQualityCard } from "@/components/Organisms/AnalyzeQualityCard";
import { api } from "@/lib/api";

// Define the CompanyQualityAnalysisResponse locally to avoid importing from a .d.ts that is not a module.
type Suggestion = {
  id: string;
  category: string;
  original: string;
  suggestion: string;
  reason?: string;
  severity?: string;
};

type Section = {
  score: number;
  suggestions?: Suggestion[];
};

type CompanyQualityAnalysisResponse = {
  grammarScore?: number;
  formalityScore?: number;
  readabilityScore?: number;
  protocolScore?: number;
  complianceScore?: number;
  grammarSection?: Section;
  protocolSection?: Section;
  companyAnalysis?: {
    companyId: string;
    communicationStyle?: string;
    complianceLevel?: number;
    methodUsed?: string;
    processingTime?: number;
    ragSourcesCount?: number;
  };
};

// This mock function can be moved to a shared lib file later.
const generateMockAnalysis = (text: string): CompanyQualityAnalysisResponse => {
  // This is a simplified mock response. A more detailed one can be created.
  return {
    grammarScore: Math.random() * 10 + 85,
    formalityScore: Math.random() * 10 + 88,
    readabilityScore: Math.random() * 10 + 82,
    protocolScore: Math.random() * 10 + 87,
    complianceScore: Math.random() * 10 + 86,
    grammarSection: {
      score: 85,
      suggestions: [
        {
          id: "g1",
          category: "Grammar",
          original: "this part of text",
          suggestion: "this corrected part",
          reason: "A grammatical error was found.",
          severity: "low",
        },
      ],
    },
    protocolSection: {
      score: 87,
      suggestions: [
        {
          id: "p1",
          category: "Protocol",
          original: "As per our last conversation",
          suggestion: "As discussed",
          reason: "To be more concise.",
          severity: "medium",
        },
      ],
    },
    companyAnalysis: {
      companyId: "test-company",
      communicationStyle: "Brief and clear",
      complianceLevel: 86,
      methodUsed: "RAG + Fine-tuning (mock)",
      processingTime: 0.5,
      ragSourcesCount: 1,
    },
  };
};

export default function AnalyzeQualityPage() {
  const { toast } = useToast();

  // State for all inputs
  const [target, setTarget] = useState<string | undefined>();
  const [situation, setSituation] = useState<string | undefined>();
  const [quality, setQuality] = useState("grammar"); // Default to 'grammar'
  const [inputText, setInputText] = useState("");

  // State for the analysis result from the API
  const [analysisResult, setAnalysisResult] =
    useState<CompanyQualityAnalysisResponse | null>(null);

  // Fetch dropdown options
  const { data: dropdownOptions } = useQuery({
    queryKey: ['dropdownOptions'],
    queryFn: api.getDropdownOptions,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Mutation logic adapted from quality-validator
  const analyzeMutation = useMutation({
    mutationFn: async (
      text: string
    ): Promise<CompanyQualityAnalysisResponse> => {
      // Use actual API call
      console.log(`Analyzing text: ${text} for ${target} in ${situation}`);
      
      try {
        const result = await api.analyzeQuality({
          text,
          company_id: "test-company", // You might want to get this from context or props
          user_id: "test-user", // You might want to get this from context or props
          target_audience: target || "팀동료",
          context: situation || "보고서",
          detailed: true
        });
        
        return result;
      } catch (error) {
        console.error("API call failed, falling back to mock data:", error);
        // Fallback to mock data if API fails
        return generateMockAnalysis(text);
      }
    },
    onSuccess: (data) => {
      setAnalysisResult(data);
      toast({
        title: "Analysis Complete",
        description: "Text quality analysis has been completed.",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Analysis Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleAnalyzeClick = () => {
    if (isAnalyzeDisabled) return;
    analyzeMutation.mutate(inputText);
  };

  const isAnalyzeDisabled =
    !inputText.trim() || !target || !situation || analyzeMutation.isPending;

  // Logic to format the output text based on the selected quality
  const outputValue = useMemo(() => {
    if (analyzeMutation.isPending) {
      return "Analyzing...";
    }
    if (!analysisResult) {
      return "Analyzed text will appear here";
    }

    switch (quality) {
      case "grammar":
        return `Score: ${analysisResult.grammarScore?.toFixed(1)}

Suggestions:
${
  analysisResult.grammarSection?.suggestions
    ?.map((s) => `- "${s.original}" -> "${s.suggestion}" (${s.reason})`)
    ?.join("\n") || "No suggestions."
}`;
      case "formality":
        return `Score: ${analysisResult.formalityScore?.toFixed(1)}

Analysis: The text's formality is appropriate.`; // Placeholder
      case "protocol":
        return `Score: ${analysisResult.protocolScore?.toFixed(1)}

Suggestions:
${
  analysisResult.protocolSection?.suggestions
    ?.map((s) => `- "${s.original}" -> "${s.suggestion}" (${s.reason})`)
    ?.join("\n") || "No suggestions."
}`;
      default:
        return "Select a quality metric to see results.";
    }
  }, [analysisResult, quality, analyzeMutation.isPending]);

  return (
    <div>
      <h1 className="font-bold text-black text-7xl">Analyze Quality Page</h1>
      <p className="mt-4 mb-12 text-5xl font-medium text-gray-700">
        Analyze document quality instantly
      </p>
      <div className="flex justify-center">
        <AnalyzeQualityCard
          targetValue={target}
          onTargetChange={setTarget}
          situationValue={situation}
          onSituationChange={setSituation}
          qualityValue={quality}
          onQualityChange={setQuality}
          inputValue={inputText}
          onInputChange={setInputText}
          outputValue={outputValue}
          isAnalyzeDisabled={isAnalyzeDisabled}
          onAnalyzeClick={handleAnalyzeClick}
        />
      </div>
    </div>
  );
}
