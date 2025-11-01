import { IsString, IsEnum, IsBoolean, IsNotEmpty, MaxLength, MinLength } from 'class-validator';

export enum TargetAudience {
  DIRECT_SUPERVISOR = '직속상사',
  TEAMMATE = '팀동료',
  OTHER_DEPARTMENT = '타부서담당자',
  CLIENT = '클라이언트',
  EXTERNAL_PARTNER = '외부협력업체',
  JUNIOR_EMPLOYEE = '후배신입',
}

export enum ContextType {
  REPORT = '보고서',
  MEETING_MINUTES = '회의록',
  EMAIL = '이메일',
  ANNOUNCEMENT = '공지사항',
  MESSAGE = '메시지',
}

export class CompanyQualityAnalysisRequestDto {
  @IsString()
  @IsNotEmpty()
  @MinLength(1)
  @MaxLength(5000)
  text: string;

  @IsEnum(TargetAudience)
  @IsNotEmpty()
  target_audience: TargetAudience;

  @IsEnum(ContextType)
  @IsNotEmpty()
  context: ContextType;

  @IsString()
  @IsNotEmpty()
  company_id: string;

  @IsString()
  @IsNotEmpty()
  user_id: string;

  @IsBoolean()
  detailed: boolean;
}
