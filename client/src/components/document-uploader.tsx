
import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, X, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export default function DocumentUploader() {
  const [files, setFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const { toast } = useToast();

  const onDrop = useCallback(
    (acceptedFiles: File[], fileRejections: any[]) => {
      const newFiles = acceptedFiles.filter(
        (file) => !files.some((f) => f.name === file.name && f.size === file.size)
      );
      setFiles((prevFiles) => [...prevFiles, ...newFiles]);

      if (fileRejections.length > 0) {
        fileRejections.forEach(({ file, errors }) => {
          errors.forEach((error: any) => {
            if (error.code === "file-too-large") {
              toast({
                variant: "destructive",
                title: "파일 크기 초과",
                description: `'${file.name}' 파일이 너무 큽니다. (최대 10MB)`,
              });
            } else if (error.code === "file-invalid-type") {
              toast({
                variant: "destructive",
                title: "지원하지 않는 파일 형식",
                description: `'${file.name}' 파일은 지원되지 않는 형식입니다.`,
              });
            } else {
              toast({
                variant: "destructive",
                title: "파일 오류",
                description: `'${file.name}' 파일을 추가할 수 없습니다.`,
              });
            }
          });
        });
      }
    },
    [files, toast]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "text/plain": [".txt"],
      "text/markdown": [".md"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
        ".docx",
      ],
    },
    maxSize: MAX_FILE_SIZE,
  });

  const removeFile = (fileToRemove: File) => {
    setFiles(files.filter((file) => file !== fileToRemove));
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      toast({
        variant: "destructive",
        title: "파일 없음",
        description: "업로드할 파일을 먼저 추가해주세요.",
      });
      return;
    }

    setIsUploading(true);
    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch("/api/v1/documents/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        toast({
          title: "업로드 성공",
          description: `${files.length}개의 파일이 성공적으로 업로드되었습니다.`,
        });
        setFiles([]);
      } else {
        let errorMessage = "파일 업로드 중 오류가 발생했습니다.";
        try {
          const contentType = response.headers.get("content-type");
          if (contentType && contentType.includes("application/json")) {
            const errorData = await response.json();
            errorMessage = errorData.detail || JSON.stringify(errorData);
          } else {
            errorMessage = await response.text();
          }
        } catch (e) {
          errorMessage = response.statusText || `HTTP error! status: ${response.status}`;
        }
        toast({
          variant: "destructive",
          title: "업로드 실패",
          description: errorMessage,
        });
      }
    } catch (error) {
      toast({
        variant: "destructive",
        title: "네트워크 오류",
        description: "서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.",
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>문서 업로드</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div
          {...getRootProps()}
          className={`flex flex-col items-center justify-center p-10 border-2 border-dashed rounded-lg cursor-pointer transition-colors
            ${
              isDragActive
                ? "border-blue-500 bg-blue-50"
                : "border-gray-300 hover:border-gray-400 hover:bg-gray-50"
            }`}
        >
          <input {...getInputProps()} />
          <Upload className="w-12 h-12 text-gray-400 mb-4" />
          <p className="text-center text-gray-500">
            여기에 파일을 드래그 앤 드롭하거나 클릭하여 파일을 선택하세요.
          </p>
          <p className="text-xs text-gray-400 mt-2">
            (PDF, TXT, MD, DOCX 파일 지원, 최대 10MB)
          </p>
        </div>

        {files.length > 0 && (
          <div className="space-y-3">
            <h3 className="font-medium">업로드할 파일:</h3>
            <ul className="space-y-2">
              {files.map((file, index) => (
                <li
                  key={index}
                  className="flex items-center justify-between p-2 bg-gray-100 rounded-md"
                >
                  <div className="flex items-center gap-3">
                    <FileText className="w-5 h-5 text-gray-600" />
                    <span className="text-sm font-medium">{file.name}</span>
                    <span className="text-xs text-gray-500">
                      ({(file.size / 1024).toFixed(2)} KB)
                    </span>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeFile(file)}
                    className="w-6 h-6"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </li>
              ))}
            </ul>
          </div>
        )}

        <Button
          onClick={handleUpload}
          disabled={isUploading || files.length === 0}
          className="w-full"
        >
          {isUploading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              업로드 중...
            </>
          ) : (
            `파일 ${files.length}개 업로드`
          )}
        </Button>
      </CardContent>
    </Card>
  );
}
