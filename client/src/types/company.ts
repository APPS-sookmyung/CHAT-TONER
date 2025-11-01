export interface CompanyProfile {
  company_id: string;
  company_name: string;
  industry: string;
  team_size: number;
  primary_business: string;
  communication_style: string;
  main_channels: string[];
  target_audience: string[];
  generated_profile: string;
  created_at: string;
  survey_data: any;
}

export interface FeedbackStats {
  total_feedback: number;
  average_rating: number;
  style_preference_stats: Record<string, number>;
}
