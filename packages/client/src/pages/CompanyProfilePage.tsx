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

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await axios.get(`/api/v1/surveys/company/${companyId}`);
        setProfile(response.data);
      } catch (err) {
        setError('Failed to fetch company profile.');
        console.error(err);
      }
      setLoading(false);
    };

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
            <h2 className="font-bold">Onboarding Characteristics</h2>
            <p className="whitespace-pre-wrap">{profile.generated_profile}</p>
          </div>
        </div>
      )}

      <div className="mt-8">
        <h2 className="text-xl font-bold mb-4">Upload PDF Documents</h2>
        {companyId && <PdfUpload companyId={companyId} />}
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
