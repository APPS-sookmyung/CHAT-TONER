import React, { useState } from 'react';
import axios from 'axios';

interface PdfUploadProps {
  companyId: string;
}

const PdfUpload: React.FC<PdfUploadProps> = ({ companyId }) => {
  const [files, setFiles] = useState<FileList | null>(null);
  const [uploadStatus, setUploadStatus] = useState<Record<string, string>>({});

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFiles(e.target.files);
  };

  const handleUpload = async () => {
    if (!files) return;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const formData = new FormData();
      formData.append('file', file);

      try {
        setUploadStatus((prev) => ({ ...prev, [file.name]: 'Uploading...' }));

        // 1. Upload the file to a temporary location
        const uploadResponse = await axios.post('/api/v1/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        const { filePath } = uploadResponse.data;

        // 2. Ingest the document from the temporary path
        await axios.post('/api/v1/rag/ingest', {
          company_id: companyId,
          folder_path: filePath,
        });

        setUploadStatus((prev) => ({ ...prev, [file.name]: 'Success' }));
      } catch (error) {
        setUploadStatus((prev) => ({ ...prev, [file.name]: 'Failed' }));
        console.error(`Failed to upload ${file.name}`, error);
      }
    }
  };

  return (
    <div>
      <input type="file" accept=".pdf" multiple onChange={handleFileChange} />
      <button onClick={handleUpload} className="bg-blue-500 text-white p-2 rounded mt-2">
        Upload
      </button>
      {files && (
        <div className="mt-4">
          {Array.from(files).map((file, i) => (
            <div key={i} className="flex justify-between items-center p-2 border-b">
              <span>{file.name}</span>
              <span>{uploadStatus[file.name]}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PdfUpload;
