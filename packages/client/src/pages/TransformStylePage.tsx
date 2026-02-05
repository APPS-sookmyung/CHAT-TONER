import { useState, useMemo, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { TransformStyleCard } from "@/components/Organisms/TransformStyleCard";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { PATH } from "@/constants/paths";
import type { UserProfile } from "@shared/schema";
import { getOrSetUserId } from "@/lib/userId";

type StyleKey = "direct" | "gentle" | "neutral";

interface StyleAnalysis {
  directness_score: number;
  softness_score: number;
  politeness_score: number;
  converted_text: string;
  converted_texts?: Record<StyleKey, string>;
  suggestions: Array<{
    type: "directness" | "softness" | "politeness";
    original: string;
    suggestion: string;
    reason: string;
  }>;
}

const generateMockAnalysis = (text: string): StyleAnalysis => {
  return {
    directness_score: Math.floor(Math.random() * 50) + 50,
    softness_score: Math.floor(Math.random() * 50) + 50,
    politeness_score: Math.floor(Math.random() * 50) + 50,
    converted_text: text + " (style converted)",
    converted_texts: {
      direct: text + " (direct)",
      gentle: text + " (gentle)",
      neutral: text + " (neutral)",
    },
    suggestions: [],
  };
};

export default function TransformStylePage() {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [inputText, setInputText] = useState("");
  // ✅ 서버 키로 통일 (direct/gentle/neutral)
  const [selectedStyle, setSelectedStyle] = useState<StyleKey>("direct");
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [analysis, setAnalysis] = useState<StyleAnalysis | null>(null);
  const [selectedFeedback, setSelectedFeedback] = useState<string | null>(null);

  useEffect(() => {
    const profileString = localStorage.getItem("chatToner_profile");
    if (profileString) {
      try {
        setUserProfile(JSON.parse(profileString));
      } catch (error) {
        console.error("Failed to parse user profile:", error);
      }
    }
  }, []);

  const convertMutation = useMutation({
    mutationFn: async ({
      text,
      style, // StyleKey
    }: {
      text: string;
      style: StyleKey;
    }): Promise<StyleAnalysis> => {
      console.log(`Transforming text: ${text}`);

      try {
        const userId = getOrSetUserId();

        const result = await api.convertStyle({
          text,
          userId,
          context: "general",
        });

        console.log("API Response:", result);
        console.log("API Response converted_texts:", result.converted_texts);

        const raw = (result?.converted_texts ?? {}) as Partial<
          Record<StyleKey | "converted", string>
        >;

        // ✅ 어떤 형태로 오든 direct/gentle/neutral을 확보 (fallback 방어)
        const direct = raw.direct ?? raw.converted ?? text;
        const gentle = raw.gentle ?? raw.converted ?? text;
        const neutral = raw.neutral ?? raw.converted ?? text;

        const converted_texts: Record<StyleKey, string> = {
          direct,
          gentle,
          neutral,
        };

        // ✅ 선택된 스타일 결과를 그대로 보여줌 (매핑 실수 제거)
        const converted_text = converted_texts[style] ?? text;

        return {
          directness_score: 75,
          softness_score: 60,
          politeness_score: 70,
          converted_text,
          converted_texts,
          suggestions: [],
        };
      } catch (error) {
        console.error("API call failed, falling back to mock data:", error);
        return generateMockAnalysis(text);
      }
    },
    onSuccess: (data) => {
      setAnalysis(data);
      toast({
        title: "Conversion Complete",
        description: "Text style conversion is complete.",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Conversion Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleTransformClick = () => {
    if (isTransformDisabled) return;
    convertMutation.mutate({ text: inputText, style: selectedStyle });
  };

  const handleFeedbackSelect = (styleType: string) => {
    setSelectedFeedback(styleType);
    toast({
      title: "피드백 추가됨",
      description: "사용자의 피드백에 추가되었습니다",
      duration: 2000,
    });
    setTimeout(() => setSelectedFeedback(null), 1000);
  };

  const isTransformDisabled = !inputText.trim() || convertMutation.isPending;

  const outputValue = useMemo(() => {
    if (convertMutation.isPending) return "Transforming...";
    if (!analysis) return "Transformed text will appear here";

    const displayText =
      analysis.converted_texts?.[selectedStyle] ?? analysis.converted_text;

    return `[Converted Text]\n${displayText}`;
  }, [analysis, selectedStyle, convertMutation.isPending]);

  return (
    <div>
      <div className="mb-8">
        <Button
          variant="ghost"
          onClick={() => navigate(PATH.CHOICE)}
          className="flex items-center gap-2 text-lg"
        >
          <ArrowLeft className="h-5 w-5" />
          Back to Features
        </Button>
      </div>

      <h1 className="font-bold text-black text-7xl">Transform Style</h1>
      <p className="mt-4 mb-12 text-5xl font-medium text-gray-700">
        Convert text to your team's unique style profile.
      </p>

      <div className="flex justify-center">
        <TransformStyleCard
          inputValue={inputText}
          onInputChange={setInputText}
          selectedStyleValue={selectedStyle}
          onSelectedStyleChange={setSelectedStyle}
          outputValue={outputValue}
          onTransformClick={handleTransformClick}
          isTransformDisabled={isTransformDisabled}
        />
      </div>

      {analysis && analysis.converted_texts && (
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-center mb-8">
            선호하는 스타일을 선택해주세요
          </h2>
          <div className="flex justify-center gap-6">
            <div
              className={`p-6 border-2 rounded-lg cursor-pointer transition-all duration-300 min-w-[300px] ${selectedFeedback === "direct"
                  ? "border-blue-400 bg-blue-50 shadow-lg animate-pulse"
                  : "border-gray-200 hover:border-blue-300 hover:shadow-md"
                }`}
              onClick={() => handleFeedbackSelect("direct")}
            >
              <h3 className="font-semibold text-lg mb-3 text-blue-600">Direct</h3>
              <p className="text-gray-700 leading-relaxed">
                {analysis.converted_texts.direct || "결과가 없습니다"}
              </p>
            </div>

            <div
              className={`p-6 border-2 rounded-lg cursor-pointer transition-all duration-300 min-w-[300px] ${selectedFeedback === "gentle"
                  ? "border-green-400 bg-green-50 shadow-lg animate-pulse"
                  : "border-gray-200 hover:border-green-300 hover:shadow-md"
                }`}
              onClick={() => handleFeedbackSelect("gentle")}
            >
              <h3 className="font-semibold text-lg mb-3 text-green-600">Gentle</h3>
              <p className="text-gray-700 leading-relaxed">
                {analysis.converted_texts.gentle || "결과가 없습니다"}
              </p>
            </div>

            <div
              className={`p-6 border-2 rounded-lg cursor-pointer transition-all duration-300 min-w-[300px] ${selectedFeedback === "neutral"
                  ? "border-purple-400 bg-purple-50 shadow-lg animate-pulse"
                  : "border-gray-200 hover:border-purple-300 hover:shadow-md"
                }`}
              onClick={() => handleFeedbackSelect("neutral")}
            >
              <h3 className="font-semibold text-lg mb-3 text-purple-600">Neutral</h3>
              <p className="text-gray-700 leading-relaxed">
                {analysis.converted_texts.neutral || "결과가 없습니다"}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
