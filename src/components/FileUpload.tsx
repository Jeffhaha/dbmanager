import React, { useState } from 'react';
import axios from 'axios';
import { Upload } from 'lucide-react';

const FileUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string>('');

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFile(event.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setUploadStatus('Please select a file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:5000/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setFile(null);
      setUploadStatus(`File uploaded successfully: ${response.data.filename}`);
      
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadStatus('An error occurred while uploading the file.');
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">File Upload</h1>
      <div className="mb-4">
        <input
          type="file"
          onChange={handleFileChange}
          value={null}
          className="block w-full text-sm text-gray-500
            file:mr-4 file:py-2 file:px-4
            file:rounded-full file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-50 file:text-blue-700
            hover:file:bg-blue-100"
        />
      </div>
      <button
        onClick={handleUpload}
        className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded inline-flex items-center"
      >
        <Upload className="w-4 h-4 mr-2" />
        Upload File
      </button>
      {uploadStatus && (
        <p className="mt-4 text-sm text-gray-600">{uploadStatus}</p>
      )}
    </div>
  );
};

export default FileUpload;