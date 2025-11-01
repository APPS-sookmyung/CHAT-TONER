import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

const CompanySurveyPage: React.FC = () => {
  const navigate = useNavigate();
  const [companyName, setCompanyName] = useState('');
  const [industry, setIndustry] = useState('');
  const [teamSize, setTeamSize] = useState(0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const companyId = uuidv4();

    try {
      await axios.post(`/api/v1/surveys/company/${companyId}/responses`, {
        company_name: companyName,
        industry,
        team_size: teamSize,
        // Add other survey fields here
      });
      navigate(`/company-profile/${companyId}`);
    } catch (error) {
      console.error('Failed to submit company survey', error);
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Company Survey</h1>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-700">Company Name</label>
          <input
            type="text"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            className="w-full p-2 border rounded"
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700">Industry</label>
          <input
            type="text"
            value={industry}
            onChange={(e) => setIndustry(e.target.value)}
            className="w-full p-2 border rounded"
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700">Team Size</label>
          <input
            type="number"
            value={teamSize}
            onChange={(e) => setTeamSize(parseInt(e.target.value, 10))}
            className="w-full p-2 border rounded"
          />
        </div>
        <button type="submit" className="bg-blue-500 text-white p-2 rounded">
          Submit Survey
        </button>
      </form>
    </div>
  );
};

export default CompanySurveyPage;
