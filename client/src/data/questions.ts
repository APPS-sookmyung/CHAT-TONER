export interface Question {
  id: string;
  category: 'company_profile' | 'communication_style';
  categoryLabel: string;
  question: string;
  description: string;
  options: string[];
  allowMultiple: boolean;
  allowCustom: boolean;
}

export const questions: Question[] = [
  // 1. 기업 프로필
  {
    id: 'company_business_category',
    category: 'company_profile',
    categoryLabel: '기업 프로필',
    question: '기업(팀)의 주요 업무 분야는 무엇입니까?',
    description: '가장 핵심적인 비즈니스 영역을 선택해주세요.',
    options: [
      'IT/소프트웨어 개발',
      '제조/생산',
      '금융/보험',
      '유통/물류',
      '미디어/콘텐츠',
      '교육/연구',
    ],
    allowMultiple: false,
    allowCustom: true
  },
  {
    id: 'company_size',
    category: 'company_profile',
    categoryLabel: '기업 프로필',
    question: '기업(팀)의 인원 수는 몇 명입니까?',
    description: '함께 일하는 동료들의 규모를 알려주세요.',
    options: [
      '1-10명',
      '11-50명',
      '51-200명',
      '201-500명',
      '501명 이상'
    ],
    allowMultiple: false,
    allowCustom: false
  },

  // 2. 소통 스타일
  {
    id: 'communication_style_overall',
    category: 'communication_style',
    categoryLabel: '소통 스타일',
    question: '기업(팀)의 전반적인 소통 문화는 어떻습니까?',
    description: '조직의 분위기와 가장 가까운 것을 선택해주세요.',
    options: [
      '수평적이고 자유로운',
      '위계적이고 체계적인',
      '친근하고 유머러스한',
      '데이터 기반의 간결한',
      '공식적이고 격식있는'
    ],
    allowMultiple: false,
    allowCustom: true
  },
  {
    id: 'main_communication_channel',
    category: 'communication_style',
    categoryLabel: '소통 스타일',
    question: '주로 사용하는 내부 소통 수단은 무엇입니까?',
    description: '가장 빈번하게 사용하는 협업 툴을 선택해주세요.',
    options: [
      'Slack',
      '이메일(Email)',
      'MS Teams',
      'Discord',
      '사내 메신저'
    ],
    allowMultiple: false,
    allowCustom: true
  },
  {
    id: 'main_communication_target',
    category: 'communication_style',
    categoryLabel: '소통 스타일',
    question: '업무상 가장 자주 소통하는 대상은 누구입니까?',
    description: '커뮤니케이션의 주된 상대를 선택해주세요.',
    options: [
      '같은 팀 내부 동료',
      '다른 팀/타 부서 담당자',
      '경영진/임원',
      '외부 고객사/클라이언트',
      '외부 협력업체'
    ],
    allowMultiple: false,
    allowCustom: false
  },
  {
    id: 'reporting_style_preference',
    category: 'communication_style',
    categoryLabel: '소통 스타일',
    question: '보고서나 회의록 작성 시 어떤 스타일을 선호하나요?',
    description: '공식 문서의 일반적인 톤앤매너를 선택해주세요.',
    options: [
      '두괄식의 핵심 요약 스타일',
      '기승전결이 뚜렷한 서사 스타일',
      '데이터와 지표 중심의 객관적 스타일',
      '정중하고 격식있는 문어체 스타일'
    ],
    allowMultiple: false,
    allowCustom: true
  },
];

export const getQuestionsByCategory = (category: Question['category']) => {
  return questions.filter(q => q.category === category);
};

export const getCategoryProgress = (category: Question['category'], responses: Record<string, any>) => {
  const categoryQuestions = getQuestionsByCategory(category);
  const answeredQuestions = categoryQuestions.filter(q => responses[q.id]);
  return {
    answered: answeredQuestions.length,
    total: categoryQuestions.length,
    percentage: Math.round((answeredQuestions.length / categoryQuestions.length) * 100)
  };
};