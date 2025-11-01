import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { CompanyProfile } from '../types/company';
import PdfUpload from '../components/PdfUpload';
import { getOrSetUserId } from '../lib/userId';
import { FeedbackStats } from '../types/company';

const CompanyProfilePage: React.FC = () => {
  const { companyId } = useParams<{ companyId: string }>();
  const [profile, setProfile] = useState<CompanyProfile | null>(null);
  const [feedbackStats, setFeedbackStats] = useState<FeedbackStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [files, setFiles] = useState<FileList | null>(null);
  const [uploadStatus, setUploadStatus] = useState<Record<string, string>>({});

  const fetchProfile = async () => {
          try {
            const response = await axios.get(`/api/v1/surveys/company/${companyId}`);
            console.log(response.data);
            setProfile(response.data);
          } catch (err) {      setError('Failed to fetch company profile.');
      console.error(err);
    }
    setLoading(false);
  };

  useEffect(() => {
    const fetchFeedbackStats = async () => {
      try {
        const userId = getOrSetUserId();
        const response = await axios.get(`/api/v1/feedback/stats/${userId}`);
        setFeedbackStats(response.data);
      } catch (err) {
        console.error('Failed to fetch feedback stats.', err);
      }
    };

    fetchProfile();
    fetchFeedbackStats();
  }, [companyId]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFiles(e.target.files);
  };

  const handleUpload = async () => {
    if (!files || !companyId) return;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const formData = new FormData();
      formData.append('file', file);

      try {
        setUploadStatus((prev) => ({ ...prev, [file.name]: 'Uploading...' }));

        const uploadResponse = await axios.post('/api/v1/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        const { filePath } = uploadResponse.data;

        await axios.post('/api/v1/rag/ingest', {
          company_id: companyId,
          folder_path: filePath,
        });

        setUploadStatus((prev) => ({ ...prev, [file.name]: 'Success' }));
        // Refresh profile to show new characteristics
        fetchProfile();
      } catch (error) {
        setUploadStatus((prev) => ({ ...prev, [file.name]: 'Failed' }));
        console.error(`Failed to upload ${file.name}`, error);
      }
    }
  };

  if (loading) {
    return <div className="p-4">Loading...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500">{error}</div>;
  }

  return (
    <div className="p-4">
      {profile && (
        <div className="bg-white shadow-md rounded-lg p-6">
          <h1 className="text-2xl font-bold mb-4">{profile.company_name}</h1>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h2 className="font-bold">Industry</h2>
              <p>{profile.industry}</p>
            </div>
            <div>
              <h2 className="font-bold">Team Size</h2>
              <p>{profile.team_size}</p>
            </div>
          </div>
          <div className="mt-4">
            <h2 className="font-bold">Survey-based Onboarding Characteristics</h2>
            <p className="whitespace-pre-wrap">
              {profile.generated_profile && profile.generated_profile.split('[자동 생성된 온보딩 특성]')[0]}
            </p>
          </div>
          {profile.generated_profile && profile.generated_profile.includes('[자동 생성된 온보딩 특성]') && (
            <div className="mt-4">
              <h2 className="font-bold">PDF-based Onboarding Characteristics</h2>
              <p className="whitespace-pre-wrap">
                {profile.generated_profile.split('[자동 생성된 온보딩 특성]')[1]}
              </p>
            </div>
          )}
        </div>
      )}

      <div className="mt-8">
        <h2 className="text-xl font-bold mb-4">Upload PDF Documents</h2>
        <PdfUpload onFileChange={handleFileChange} onUpload={handleUpload} />
        <div className="mt-4">
          {files ? (
            Array.from(files).map((file, i) => (
              <div key={i} className="flex justify-between items-center p-2 border-b">
                <span>{file.name}</span>
                <span>{uploadStatus[file.name]}</span>
              </div>
            ))
          ) : (
            <p>No files selected.</p>
          )}
        </div>
      </div>

      {feedbackStats && (
        <div className="mt-8 bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Feedback Statistics</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="font-bold">Total Feedback</h3>
              <p>{feedbackStats.total_feedback}</p>
            </div>
            <div>
              <h3 className="font-bold">Average Rating</h3>
              <p>{feedbackStats.average_rating.toFixed(1)}</p>
            </div>
          </div>
          <div className="mt-4">
            <h3 className="font-bold">Style Preferences</h3>
            <ul>
              {Object.entries(feedbackStats.style_preference_stats).map(([style, count]) => (
                <li key={style}>{style}: {count}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default CompanyProfilePage;

