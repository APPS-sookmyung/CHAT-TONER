import DocumentUploader from "@/components/document-uploader";
import PDFSummarizer from "@/components/pdf-summarizer";

export default function UploadPage() {
  return (
    <div className="w-screen px-[50px] py-10 space-y-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold text-gray-900">Document Management</h1>
          <p className="text-gray-600">Upload and analyze your PDF documents</p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div>
            <DocumentUploader />
          </div>

          {/* Summarize Section */}
          <div>
            <PDFSummarizer />
          </div>
        </div>
      </div>
    </div>
  );
}
