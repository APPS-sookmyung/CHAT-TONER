import { useState, useId } from "react";
import { useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ThumbsUp, ThumbsDown, Lightbulb, Check, Wand2, FileText, Copy } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import type { 
  CompanyQualityAnalysisResponse, 
  CompanySuggestionItem, 
  FinalTextGenerationRequest, 
  UserFeedbackRequest,
  GrammarSection,
  ProtocolSection,
  TargetAudience,
  ContextType
} from "@shared/schema";

// Props Interfaces
interface QualityAnalysisResultProps {
  originalText: string;
  analysisResult: CompanyQualityAnalysisResponse;
  targetAudience: TargetAudience;
  context: ContextType;
  userId: string;
  companyId: string;
  onApplySuggestion: (original: string, suggestion: string) => void;
}

interface SuggestionsTabProps {
  section: GrammarSection | ProtocolSection;
  selectedIds: Set<string>;
  onSelect: (id: string) => void;
  onApplySuggestion: (original: string, suggestion: string) => void;
  targetAudience: TargetAudience;
  context: ContextType;
  sessionId: string;
  userId: string;
  companyId: string;
}

interface SuggestionItemProps {
  item: CompanySuggestionItem;
  isSelected: boolean;
  onSelect: (id: string) => void;
  onApply: () => void;
  targetAudience: TargetAudience;
  context: ContextType;
  sessionId: string;
  userId: string;
  companyId: string;
}

// Main Component
export default function QualityAnalysisResult({ 
  originalText, 
  analysisResult, 
  onApplySuggestion,
  targetAudience,
  context,
  userId,
  companyId
}: QualityAnalysisResultProps) {
  const { toast } = useToast();
  const [selectedGrammarIds, setSelectedGrammarIds] = useState<Set<string>>(new Set());
  const [selectedProtocolIds, setSelectedProtocolIds] = useState<Set<string>>(new Set());
  const [finalText, setFinalText] = useState<string | null>(null);
  const sessionId = useId();

  const handleSelectSuggestion = (suggestionId: string, section: 'grammar' | 'protocol') => {
    const newSet = section === 'grammar' ? new Set(selectedGrammarIds) : new Set(selectedProtocolIds);
    if (newSet.has(suggestionId)) {
      newSet.delete(suggestionId);
    } else {
      newSet.add(suggestionId);
    }
    if (section === 'grammar') {
      setSelectedGrammarIds(newSet);
    } else {
      setSelectedProtocolIds(newSet);
    }
  };

  const generateFinalMutation = useMutation({
    mutationFn: async (data: FinalTextGenerationRequest) => {
      const res = await fetch('/api/v1/quality/company/generate-final', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error('Failed to generate final version.');
      return res.json();
    },
    onSuccess: (data) => {
      setFinalText(data.finalText);
      toast({ title: "Success", description: "The final version has been generated." });
    },
    onError: (error: any) => {
      toast({ title: "Error", description: error.message, variant: "destructive" });
    }
  });

  const handleGenerateFinal = () => {
    generateFinalMutation.mutate({
      original_text: originalText,
      grammar_suggestions: analysisResult.grammarSection.suggestions,
      protocol_suggestions: analysisResult.protocolSection.suggestions,
      selected_grammar_ids: Array.from(selectedGrammarIds),
      selected_protocol_ids: Array.from(selectedProtocolIds),
      user_id: userId,
      company_id: companyId,
    });
  };

  return (
    <Tabs defaultValue="overview" className="w-full">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="overview">Overview</TabsTrigger>
        <TabsTrigger value="grammar">Grammar ({analysisResult.grammarSection.suggestions.length})</TabsTrigger>
        <TabsTrigger value="protocol">Protocol ({analysisResult.protocolSection.suggestions.length})</TabsTrigger>
      </TabsList>

      <TabsContent value="overview">
        <OverviewTab 
          analysisResult={analysisResult} 
          onGenerateFinal={handleGenerateFinal} 
          isGenerating={generateFinalMutation.isPending}
          finalText={finalText}
        />
      </TabsContent>

      <TabsContent value="grammar">
        <SuggestionsTab
          section={analysisResult.grammarSection}
          selectedIds={selectedGrammarIds}
          onSelect={id => handleSelectSuggestion(id, 'grammar')}
          onApplySuggestion={onApplySuggestion}
          targetAudience={targetAudience}
          context={context}
          sessionId={sessionId}
          userId={userId}
          companyId={companyId}
        />
      </TabsContent>

      <TabsContent value="protocol">
        <SuggestionsTab
          section={analysisResult.protocolSection}
          selectedIds={selectedProtocolIds}
          onSelect={id => handleSelectSuggestion(id, 'protocol')}
          onApplySuggestion={onApplySuggestion}
          targetAudience={targetAudience}
          context={context}
          sessionId={sessionId}
          userId={userId}
          companyId={companyId}
        />
      </TabsContent>
    </Tabs>
  );
}

// Sub-components
function OverviewTab({ analysisResult, onGenerateFinal, isGenerating, finalText }: any) {
  const { toast } = useToast();
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!finalText) return;
    navigator.clipboard.writeText(finalText);
    setCopied(true);
    toast({ title: "Copy complete!" });
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card>
      <CardHeader><CardTitle>Overall Analysis Results</CardTitle></CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <ScoreDisplay name="Overall Compliance" score={analysisResult.complianceScore} />
          <ScoreDisplay name="Grammar" score={analysisResult.grammarScore} />
          <ScoreDisplay name="Formality" score={analysisResult.formalityScore} />
          <ScoreDisplay name="Protocol" score={analysisResult.protocolScore} />
        </div>
        <Button onClick={onGenerateFinal} disabled={isGenerating} className="w-full">
          {isGenerating ? 'Generating...' : 'Generate final version with selected suggestions'}
        </Button>
        {finalText && (
          <div className="pt-4 space-y-2">
            <h3 className="font-semibold">Final generated text:</h3>
            <div className="border rounded-md p-4 bg-gray-50 relative">
              <p className="text-gray-800 whitespace-pre-wrap">{finalText}</p>
              <Button variant="ghost" size="icon" className="absolute top-2 right-2" onClick={handleCopy}>
                {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function ScoreDisplay({ name, score }: { name: string, score: number }) {
    return (
        <div className="p-4 bg-gray-100 rounded-lg">
            <p className="text-sm text-gray-600">{name}</p>
            <p className="text-2xl font-bold text-blue-600">{Math.round(score)}</p>
        </div>
    )
}

function SuggestionsTab({ section, selectedIds, onSelect, onApplySuggestion, targetAudience, context, sessionId, userId, companyId }: SuggestionsTabProps) {
  const category = section.suggestions[0]?.category || 'Suggestion';
  
  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
            <CardTitle className="flex items-center gap-2">
                {category === 'Grammar' ? <FileText /> : <Wand2 />}
                {category} Details
            </CardTitle>
            <p>Score: <span className="font-bold text-blue-600">{Math.round(section.score)}</span></p>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {section.suggestions.length > 0 ? (
          section.suggestions.map((item: CompanySuggestionItem) => (
            <SuggestionItem
              key={item.id}
              item={item}
              isSelected={selectedIds.has(item.id)}
              onSelect={onSelect}
              onApply={() => onApplySuggestion(item.original, item.suggestion)}
              targetAudience={targetAudience}
              context={context}
              sessionId={sessionId}
              userId={userId}
              companyId={companyId}
            />
          ))
        ) : (
          <p className="text-center text-gray-500 py-8">There are no suggestions.</p>
        )}
      </CardContent>
    </Card>
  );
}

function SuggestionItem({ item, isSelected, onSelect, onApply, targetAudience, context, sessionId, userId, companyId }: SuggestionItemProps) {
  const { toast } = useToast();
  const feedbackMutation = useMutation({
    mutationFn: async (data: { feedback_value: 'good' | 'bad' }) => {
        if (!userId || !companyId) {
          toast({ title: "Error", description: "Cannot send feedback because user or company ID is missing.", variant: "destructive" });
          return;
        }

        const feedbackData: UserFeedbackRequest = {
            user_id: userId,
            company_id: companyId,
            session_id: sessionId,
            original_text: item.original,
            suggested_text: item.suggestion,
            feedback_type: item.category === 'Grammar' ? 'grammar' : 'protocol',
            feedback_value: data.feedback_value,
            target_audience: targetAudience,
            context: context,
            suggestion_category: item.category,
        };

        const res = await fetch('/api/v1/quality/company/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(feedbackData),
        });
        if (!res.ok) throw new Error('Failed to submit feedback.');
        return res.json();
    },
    onSuccess: () => {
        toast({ title: "Feedback has been submitted.", description: "Thank you for your valuable feedback." });
    },
    onError: (error: any) => {
        toast({ title: "Error", description: error.message, variant: "destructive" });
    }
  });

  return (
    <div className={`border rounded-lg p-4 space-y-3 transition-colors ${isSelected ? 'bg-blue-50 border-blue-200' : ''}`}>
      <div className="flex items-start justify-between">
        <div className="space-y-2 flex-1">
            <div>
                <span className="text-xs text-gray-500">Original: </span>
                <span className="text-gray-700 line-through">{item.original}</span>
            </div>
            <div>
                <span className="text-xs text-gray-500">Suggestion: </span>
                <span className="text-blue-600 font-medium">{item.suggestion}</span>
            </div>
        </div>
        <div className="flex items-center gap-2 ml-4">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => onSelect(item.id)}
            className={isSelected ? 'text-blue-600 border-blue-400' : ''}
          >
            <Check className="w-4 h-4 mr-2" />
            {isSelected ? 'Selected' : 'Select'}
          </Button>
          <Button variant="ghost" size="icon" onClick={() => feedbackMutation.mutate({ feedback_value: 'good' })}>
            <ThumbsUp className="w-4 h-4 text-gray-500 hover:text-green-600" />
          </Button>
          <Button variant="ghost" size="icon" onClick={() => feedbackMutation.mutate({ feedback_value: 'bad' })}>
            <ThumbsDown className="w-4 h-4 text-gray-500 hover:text-red-600" />
          </Button>
        </div>
      </div>
      <div className="text-sm text-gray-600 bg-gray-50 p-2 rounded-md">
        <Lightbulb className="w-4 h-4 inline-block mr-2 text-yellow-500" />
        <strong>Reason:</strong> {item.reason}
      </div>
    </div>
  );
}