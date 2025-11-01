import React from 'react';

interface PdfUploadProps {
  onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onUpload: () => void;
}

const PdfUpload: React.FC<PdfUploadProps> = ({ onFileChange, onUpload }) => {
  return (
    <div>
      <input type="file" accept=".pdf" multiple onChange={onFileChange} />
      <button onClick={onUpload} className="bg-blue-500 text-white p-2 rounded mt-2">
        Upload
      </button>
    </div>
  );
};

export default PdfUpload;
