import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { getOrSetUserId } from '../lib/userId';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Button } from '@/components/ui/button';
import { Building2, Users, Mail, Target, Calendar, FileText, Trash2, Upload, Plus, Home, MessageSquare } from 'lucide-react';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { useNavigate } from 'react-router-dom';
import { PATH } from '@/constants/paths';

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
  const navigate = useNavigate();
  const { toast } = useToast();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [documents, setDocuments] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [documentsLoading, setDocumentsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 문서 목록 조회
  const fetchDocuments = async () => {
    setDocumentsLoading(true);
    try {
      const docs = await api.getDocuments();
      setDocuments(docs);
    } catch (err) {
      console.error('문서 목록 로딩 실패:', err);
      toast({
        variant: "destructive",
        title: "문서 목록 로딩 실패",
        description: "문서 목록을 불러오는데 실패했습니다.",
      });
    } finally {
      setDocumentsLoading(false);
    }
  };

  // 문서 삭제
  const handleDeleteDocument = async (documentName: string) => {
    if (!confirm(`"${documentName}" 문서를 삭제하시겠습니까?`)) {
      return;
    }

    try {
      await api.deleteDocument(documentName);
      toast({
        title: "문서 삭제 완료",
        description: `"${documentName}" 문서가 삭제되었습니다.`,
      });
      fetchDocuments(); // 목록 새로고침
    } catch (err) {
      console.error('문서 삭제 실패:', err);
      toast({
        variant: "destructive",
        title: "문서 삭제 실패",
        description: "문서를 삭제하는데 실패했습니다.",
      });
    }
  };

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

        // 문서 목록도 함께 로드
        fetchDocuments();

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
        <div className="flex justify-end gap-3 mb-4">
          <Button
            variant="outline"
            onClick={() => navigate(PATH.HOME)}
            className="flex items-center gap-2"
          >
            <Home className="h-4 w-4" />
            홈으로
          </Button>
          <Button
            onClick={() => navigate(PATH.CHOICE)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white"
          >
            <MessageSquare className="h-4 w-4" />
            Use ChatToner
          </Button>
        </div>
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
      {/* 상단 네비게이션 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">내 커뮤니케이션 프로필</h1>
          <p className="text-gray-600">팀 특성에 맞는 맞춤형 커뮤니케이션 가이드</p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={() => navigate(PATH.HOME)}
            className="flex items-center gap-2"
          >
            <Home className="h-4 w-4" />
            홈으로
          </Button>
          <Button
            onClick={() => navigate(PATH.CHOICE)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white"
          >
            <MessageSquare className="h-4 w-4" />
            Use ChatToner
          </Button>
        </div>
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
      <Card className="mb-6">
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

      {/* 기업 데이터 관리 */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              기업 데이터 관리
            </CardTitle>
            <CardDescription>
              업로드된 기업 문서와 데이터를 관리합니다.
            </CardDescription>
          </div>
          <Button
            onClick={() => navigate('/upload')}
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            문서 업로드
          </Button>
        </CardHeader>
        <CardContent>
          {documentsLoading ? (
            <div className="flex items-center justify-center py-4">
              <p className="text-gray-500">문서 목록 로딩 중...</p>
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 mb-4">업로드된 문서가 없습니다.</p>
              <Button
                onClick={() => navigate('/upload')}
                variant="outline"
                className="flex items-center gap-2 mx-auto"
              >
                <Upload className="h-4 w-4" />
                문서 업로드 시작하기
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex justify-between items-center mb-4">
                <p className="text-sm text-gray-600">
                  총 {documents.length}개의 문서가 업로드되어 있습니다.
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={fetchDocuments}
                  disabled={documentsLoading}
                >
                  새로고침
                </Button>
              </div>

              <div className="space-y-2 max-h-96 overflow-y-auto">
                {documents.map((doc, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <FileText className="h-5 w-5 text-blue-600" />
                      <div>
                        <p className="font-medium text-sm">{doc}</p>
                        <p className="text-xs text-gray-500">
                          {doc.endsWith('.pdf') ? 'PDF 문서' :
                           doc.endsWith('.docx') ? 'Word 문서' :
                           doc.endsWith('.txt') ? '텍스트 파일' :
                           doc.endsWith('.md') ? 'Markdown 파일' : '문서'}
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteDocument(doc)}
                      className="text-red-600 hover:text-red-800 hover:bg-red-50"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ProfilePage;