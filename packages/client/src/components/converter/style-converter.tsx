"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import type { UserProfile } from "@shared/schema";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Zap,
  Feather,
  Hand,
  Wand2,
  CheckCircle,
  Lightbulb,
  Copy,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface StyleConverterProps {
  userProfile: UserProfile;
}

interface StyleAnalysis {
  directness_score: number;
  softness_score: number;
  politeness_score: number;
  converted_text: string;
  suggestions: Array<{ 
    type: "directness" | "softness" | "politeness";
    original: string;
    suggestion: string;
    reason: string;
  }>;
}

// Temporary mock data generation function
const generateMockAnalysis = (text: string): StyleAnalysis => {
  return {
    directness_score: Math.floor(Math.random() * 50) + 50,
    softness_score: Math.floor(Math.random() * 50) + 50,
    politeness_score: Math.floor(Math.random() * 50) + 50,
    converted_text: text + " (style converted)",
    suggestions: [
      {
        type: "directness",
        original: "this part",
        suggestion: "that part",
        reason: "Changed to a more direct expression to clarify the meaning.",
      },
      {
        type: "softness",
        original: "do it",
        suggestion: "Could you do it for me?",
        reason: "Changed to a softer expression to give a friendly feeling.",
      },
      {
        type: "politeness",
        original: "Hey",
        suggestion: "",
        reason: "Changed to a more polite expression to be respectful.",
      },
    ],
  };
};

export default function StyleConverter({ userProfile }: StyleConverterProps) {
  const [inputText, setInputText] = useState("");
  const [analysis, setAnalysis] = useState<StyleAnalysis | null>(null);
  const { toast } = useToast();

  const convertMutation = useMutation({
    mutationFn: async (text: string): Promise<StyleAnalysis> => {
      // TODO: Replace with actual style conversion API call logic.
      // const { rag } = await import("@/lib/rag");
      // const result = await rag.convertText({ query: text, user_profile: userProfile });

      // Currently returns mock data after 2 seconds.
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve(generateMockAnalysis(text));
        }, 2000);
      });
    },
    onSuccess: (data) => {
      setAnalysis(data);
      toast({
        title: "Conversion Complete",
        description: "Text style conversion is complete.",
      });
    },
    onError: (error) => {
      toast({
        title: "Conversion Failed",
        description:
          error instanceof Error
            ? error.message
            : "An unknown error has occurred.",
        variant: "destructive",
      });
    },
  });

  const handleConvert = () => {
    if (!inputText.trim()) {
      toast({
        title: "Please enter text",
        description: "Please enter the text to convert.",
        variant: "destructive",
      });
      return;
    }
    convertMutation.mutate(inputText.trim());
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copy Complete",
      description: "The text has been copied to the clipboard.",
    });
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-blue-600";
    if (score >= 40) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreBadge = (score: number) => {
    if (score >= 80)
      return <Badge className="bg-green-100 text-green-800">Very High</Badge>;
    if (score >= 60)
      return <Badge className="bg-blue-100 text-blue-800">High</Badge>;
    if (score >= 40)
      return <Badge className="bg-yellow-100 text-yellow-800">Moderate</Badge>;
    return <Badge className="bg-red-100 text-red-800">Low</Badge>;
  };

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wand2 className="w-5 h-5" />
            Text to Convert
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="Enter the text to convert the style...\nWe will convert it to a new style that matches your profile."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            className="min-h-[150px]"
          />
          <Button
            onClick={handleConvert}
            disabled={convertMutation.isPending}
            className="w-full"
          >
            {convertMutation.isPending ? "Converting..." : "Convert Style"}
          </Button>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysis && (
        <div className="space-y-6">
          {/* Converted Text Display */}
          <Card className="bg-gradient-to-br from-white to-sky-50/30 border-sky-100/50 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sky-700">
                <CheckCircle className="w-5 h-5" />
                Converted Text
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-sky-50 rounded-lg p-4 border border-sky-200">
                <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                  {analysis.converted_text}
                </p>
              </div>
              <div className="flex gap-2 mt-4">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => copyToClipboard(analysis.converted_text!)}
                  className="hover:bg-gradient-to-r hover:from-sky-50 hover:to-blue-50 hover:border-sky-300 transition-all duration-300"
                >
                  <Copy className="w-4 h-4 mr-2" />
                  Copy
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Score Cards */}
          <div className="grid md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-6 text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Zap className="w-5 h-5 text-red-600" />
                  <h3 className="font-semibold">Directness</h3>
                </div>
                <div
                  className={`text-3xl font-bold ${getScoreColor(
                    analysis.directness_score
                  )}`}
                >
                  {Math.round(analysis.directness_score)}
                </div>
                <div className="text-sm text-gray-600">/ 100</div>
                {getScoreBadge(analysis.directness_score)}
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Feather className="w-5 h-5 text-green-600" />
                  <h3 className="font-semibold">Softness</h3>
                </div>
                <div
                  className={`text-3xl font-bold ${getScoreColor(
                    analysis.softness_score
                  )}`}
                >
                  {Math.round(analysis.softness_score)}
                </div>
                <div className="text-sm text-gray-600">/ 100</div>
                {getScoreBadge(analysis.softness_score)}
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Hand className="w-5 h-5 text-blue-600" />
                  <h3 className="font-semibold">Politeness</h3>
                </div>
                <div
                  className={`text-3xl font-bold ${getScoreColor(
                    analysis.politeness_score
                  )}`}
                >
                  {Math.round(analysis.politeness_score)}
                </div>
                <div className="text-sm text-gray-600">/ 100</div>
                {getScoreBadge(analysis.politeness_score)}
              </CardContent>
            </Card>
          </div>

          {/* Suggestions */}
          {analysis.suggestions.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="w-5 h-5" />
                  Style Improvement Suggestions ({analysis.suggestions.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analysis.suggestions.map((suggestion, index) => (
                    <div
                      key={index}
                      className="border border-gray-200 rounded-lg p-4"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <Badge variant="outline" className="capitalize">
                          {suggestion.type}
                        </Badge>
                      </div>
                      <div className="space-y-2">
                        <div>
                          <span className="text-sm text-gray-600">Original: </span>
                          <span className="text-gray-800">
                            {suggestion.original}
                          </span>
                        </div>
                        <div>
                          <span className="text-sm text-gray-600">Suggestion: </span>
                          <span className="text-green-600 font-medium">
                            {suggestion.suggestion}
                          </span>
                        </div>
                        <div>
                          <span className="text-sm text-gray-600">Reason: </span>
                          <span className="text-gray-700">
                            {suggestion.reason}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
