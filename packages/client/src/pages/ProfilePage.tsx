import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { getOrSetUserId } from '../lib/userId';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Building2, Users, Mail, Target, Calendar } from 'lucide-react';

interface CompanyContext {
  companySize: string;
  teamSize: string;
  primaryFunction: string;
  communicationStyle: string;
  primaryChannel: string;
  primaryAudience: string[];
  sizeCharacteristics: string[];
  functionCharacteristics: string[];
}

interface UserProfile {
  id: number;
  userId: string;
  companyProfile: string;
  companyContext: CompanyContext;
  surveyResponses: Record<string, any>;
  createdAt: string;
  profileType: string;
}

const ProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const userId = getOrSetUserId();

        // 먼저 기존 프로필 API 확인 (기존 말투 프로필)
        try {
          const profileResponse = await axios.get(`/api/v1/profile/${userId}`);
          if (profileResponse.data) {
            console.log('기존 프로필 발견:', profileResponse.data);
          }
        } catch (err) {
          console.log('기존 프로필 없음');
        }

        // 새로운 회사 프로필 API 확인
        const companyProfileResponse = await axios.get(`/api/v1/company-profile/${userId}`);
        setProfile(companyProfileResponse.data);

      } catch (err) {
        console.error('프로필 로딩 실패:', err);
        setError('프로필을 불러오는데 실패했습니다. 설문을 먼저 완료해주세요.');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatProfile = (profileText: string) => {
    // 마크다운 형식을 HTML로 간단 변환
    return profileText
      .replace(/### (.*)/g, '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/- \*\*(.*?)\*\*/g, '• <strong>$1</strong>')
      .replace(/\n\n/g, '</p><p class="mb-3">')
      .replace(/\n/g, '<br>');
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">프로필을 불러오는 중...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Card>
          <CardHeader>
            <CardTitle className="text-red-600">프로필을 찾을 수 없음</CardTitle>
            <CardDescription>
              {error || '프로필이 존재하지 않습니다.'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              커뮤니케이션 가이드를 생성하려면 먼저 설문을 완료해주세요.
            </p>
            <a
              href="/survey/1"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              설문 시작하기
            </a>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">내 커뮤니케이션 프로필</h1>
        <p className="text-gray-600">팀 특성에 맞는 맞춤형 커뮤니케이션 가이드</p>
      </div>

      {/* 회사 정보 요약 */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            팀 정보
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-gray-500" />
              <div>
                <p className="text-sm text-gray-500">팀 규모</p>
                <p className="font-medium">{profile.companyContext.companySize}</p>
                <p className="text-xs text-gray-400">({profile.companyContext.teamSize}명)</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-gray-500" />
              <div>
                <p className="text-sm text-gray-500">주요 업무</p>
                <p className="font-medium capitalize">{profile.companyContext.primaryFunction}</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Mail className="h-4 w-4 text-gray-500" />
              <div>
                <p className="text-sm text-gray-500">주요 채널</p>
                <p className="font-medium capitalize">{profile.companyContext.primaryChannel}</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-gray-500" />
              <div>
                <p className="text-sm text-gray-500">생성일</p>
                <p className="font-medium">{formatDate(profile.createdAt)}</p>
              </div>
            </div>
          </div>

          <Separator className="my-4" />

          <div className="space-y-3">
            <div>
              <p className="text-sm font-medium mb-2">팀 특성</p>
              <div className="flex flex-wrap gap-2">
                {profile.companyContext.sizeCharacteristics.map((char, index) => (
                  <Badge key={index} variant="secondary">{char}</Badge>
                ))}
              </div>
            </div>

            <div>
              <p className="text-sm font-medium mb-2">업무 특성</p>
              <div className="flex flex-wrap gap-2">
                {profile.companyContext.functionCharacteristics.map((char, index) => (
                  <Badge key={index} variant="outline">{char}</Badge>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 커뮤니케이션 가이드 */}
      <Card>
        <CardHeader>
          <CardTitle>커뮤니케이션 가이드</CardTitle>
          <CardDescription>
            팀 규모와 업무 특성을 고려한 맞춤형 소통 가이드입니다.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            className="prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{
              __html: `<p class="mb-3">${formatProfile(profile.companyProfile)}</p>`
            }}
          />
        </CardContent>
      </Card>
    </div>
  );
};

export default ProfilePage;