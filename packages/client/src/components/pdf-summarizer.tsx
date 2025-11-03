import { useState, useEffect } from "react";
import { FileText, Loader2, BookOpen, ArrowRight, Download, AlertCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";

interface DocumentSummary {
  success: boolean;
  file_name: string;
  summary: string;
  summary_type: string;
  original_length: number;
  summary_length: number;
  error?: string;
}

export default function PDFSummarizer() {
  const [documents, setDocuments] = useState<string[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<string>("");
  const [summaryType, setSummaryType] = useState<"brief" | "detailed" | "bullet_points">("brief");
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingDocs, setIsLoadingDocs] = useState(false);
  const [summary, setSummary] = useState<DocumentSummary | null>(null);
  const { toast } = useToast();

  // Load documents on component mount
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setIsLoadingDocs(true);
    try {
      const result = await api.getDocuments();
      // Filter for PDF files only
      const pdfFiles = result.filter((doc: string) => doc.toLowerCase().endsWith('.pdf'));
      setDocuments(pdfFiles);
    } catch (error: any) {
      console.error("Error loading documents:", error);
      toast({
        variant: "destructive",
        title: "Error loading documents",
        description: "Could not load document list. Please try again later.",
      });
    } finally {
      setIsLoadingDocs(false);
    }
  };

  const handleSummarize = async () => {
    if (!selectedDocument) {
      toast({
        variant: "destructive",
        title: "No document selected",
        description: "Please select a PDF document to summarize.",
      });
      return;
    }

    setIsLoading(true);
    setSummary(null);

    try {
      const result = await api.summarizePDF({
        document_name: selectedDocument,
        summary_type: summaryType,
      });

      setSummary(result);

      if (result.success) {
        toast({
          title: "Summary generated",
          description: `Successfully summarized ${result.file_name}`,
        });
      } else {
        toast({
          variant: "destructive",
          title: "Summarization failed",
          description: result.error || "Could not generate summary. Please try again.",
        });
      }
    } catch (error: any) {
      console.error("Summarization error:", error);
      toast({
        variant: "destructive",
        title: "Summarization failed",
        description: error.response?.data?.detail || "Could not generate summary. Please try again later.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleExportSummary = () => {
    if (!summary?.success) return;

    const exportData = {
      file_name: summary.file_name,
      summary_type: summary.summary_type,
      summary: summary.summary,
      original_length: summary.original_length,
      summary_length: summary.summary_length,
      generated_at: new Date().toISOString(),
    };

    const dataStr = JSON.stringify(exportData, null, 2);
    const url = URL.createObjectURL(
      new Blob([dataStr], { type: "application/json" })
    );
    const a = document.createElement("a");
    a.href = url;
    a.download = `${summary.file_name.replace('.pdf', '')}-summary-${summary.summary_type}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getSummaryTypeDescription = (type: string) => {
    switch (type) {
      case "brief":
        return "Simple 2-3 sentence overview";
      case "detailed":
        return "Comprehensive section-by-section summary";
      case "bullet_points":
        return "Key points in bullet format";
      default:
        return "";
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="w-5 h-5" />
            PDF Document Summarizer
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Document Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Select PDF Document</label>
            <div className="flex gap-2">
              <Select value={selectedDocument} onValueChange={setSelectedDocument} disabled={isLoadingDocs}>
                <SelectTrigger className="flex-1">
                  <SelectValue
                    placeholder={
                      isLoadingDocs
                        ? "Loading documents..."
                        : documents.length === 0
                          ? "No PDF documents found"
                          : "Choose a PDF document"
                    }
                  />
                </SelectTrigger>
                <SelectContent>
                  {documents.map((doc) => (
                    <SelectItem key={doc} value={doc}>
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4" />
                        {doc}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button variant="outline" onClick={loadDocuments} disabled={isLoadingDocs}>
                {isLoadingDocs ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  "Refresh"
                )}
              </Button>
            </div>
            {documents.length === 0 && !isLoadingDocs && (
              <p className="text-sm text-muted-foreground flex items-center gap-1">
                <AlertCircle className="w-4 h-4" />
                No PDF documents found. Upload some PDF files first.
              </p>
            )}
          </div>

          {/* Summary Type Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Summary Type</label>
            <Select value={summaryType} onValueChange={(value) => setSummaryType(value as "brief" | "detailed" | "bullet_points")}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="brief">
                  <div className="space-y-1">
                    <div className="font-medium">Brief</div>
                    <div className="text-xs text-muted-foreground">Simple 2-3 sentence overview</div>
                  </div>
                </SelectItem>
                <SelectItem value="detailed">
                  <div className="space-y-1">
                    <div className="font-medium">Detailed</div>
                    <div className="text-xs text-muted-foreground">Comprehensive section-by-section summary</div>
                  </div>
                </SelectItem>
                <SelectItem value="bullet_points">
                  <div className="space-y-1">
                    <div className="font-medium">Bullet Points</div>
                    <div className="text-xs text-muted-foreground">Key points in bullet format</div>
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Generate Summary Button */}
          <Button
            onClick={handleSummarize}
            disabled={isLoading || !selectedDocument}
            className="w-full"
            size="lg"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Generating Summary...
              </>
            ) : (
              <>
                <ArrowRight className="w-4 h-4 mr-2" />
                Generate {summaryType.charAt(0).toUpperCase() + summaryType.slice(1)} Summary
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Summary Results */}
      {summary && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Summary Results
            </CardTitle>
            {summary.success && (
              <Button variant="outline" size="sm" onClick={handleExportSummary}>
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
            )}
          </CardHeader>
          <CardContent className="space-y-4">
            {summary.success ? (
              <>
                {/* Summary Metadata */}
                <div className="flex flex-wrap gap-2 p-3 bg-muted/50 rounded-lg">
                  <Badge variant="secondary">{summary.file_name}</Badge>
                  <Badge variant="outline">{summary.summary_type}</Badge>
                  <Badge variant="outline">
                    {summary.original_length} → {summary.summary_length} chars
                  </Badge>
                  <Badge variant="outline">
                    {Math.round((summary.summary_length / summary.original_length) * 100)}% compression
                  </Badge>
                </div>

                {/* Summary Content */}
                <div className="space-y-2">
                  <h4 className="font-medium">Summary ({getSummaryTypeDescription(summary.summary_type)})</h4>
                  <div className="p-4 bg-muted/30 rounded-lg border-l-4 border-blue-500">
                    <div className="whitespace-pre-wrap text-sm leading-relaxed">
                      {summary.summary}
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
                <AlertCircle className="w-5 h-5" />
                <div>
                  <div className="font-medium">Summarization failed</div>
                  <div className="text-sm">{summary.error || "An error occurred while generating the summary."}</div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}