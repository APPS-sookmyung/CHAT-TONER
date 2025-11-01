import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle, Download, Sparkles } from "lucide-react";
import { analyzeUserProfile } from "@/lib/prompt-engineering";
import type { UserProfile } from "@shared/schema";

interface ResultsSummaryProps {
  userProfile: UserProfile;
  completionRate: number;
  onStartConversion: () => void;
  onExportData: () => void;
}

export default function ResultsSummary({ 
  userProfile, 
  completionRate, 
  onStartConversion, 
  onExportData 
}: ResultsSummaryProps) {
  const analysis = analyzeUserProfile(userProfile);

  return (
    <Card className="shadow-sm border border-gray-200">
      <CardContent className="p-8 text-center">
        <div className="mb-6">
          <div className="w-16 h-16 bg-success/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="text-success w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Profile Collection Complete!</h2>
          <p className="text-gray-600">Your unique tone and style have been successfully analyzed.</p>
        </div>
        
        <div className="bg-gray-50 rounded-xl p-6 mb-6">
          <h3 className="font-semibold text-gray-900 mb-4">Summary of Collected Data</h3>
          <div className="grid md:grid-cols-2 gap-4 text-left">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Response Completion Rate:</span>
              <span className="font-medium text-success">{completionRate}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Preferred Formality:</span>
              <span className="font-medium">{analysis.formalityDescription}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Preferred Friendliness:</span>
              <span className="font-medium">{analysis.friendlinessDescription}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Emotional Expression:</span>
              <span className="font-medium">{analysis.emotionDescription}</span>
            </div>
            {analysis.usesEmoticons && (
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Special Preference:</span>
                <span className="font-medium">Use of Emoticons</span>
              </div>
            )}
            {analysis.usesAbbreviations && (
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Linguistic Characteristics:</span>
                <span className="font-medium">Preference for Abbreviations</span>
              </div>
            )}
          </div>
        </div>
        
        <div className="flex justify-center space-x-4">
          <Button
            variant="outline"
            onClick={onExportData}
            className="flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Export Data</span>
          </Button>
          <Button
            onClick={onStartConversion}
            className="flex items-center space-x-2 px-8"
          >
            <Sparkles className="w-4 h-4" />
            <span>Start Text Conversion</span>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
