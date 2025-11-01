import { IsString, IsNumber, IsEnum, IsArray, IsObject, ValidateNested, IsInt } from 'class-validator';
import { Type } from 'class-transformer';

export enum SeverityLevel {
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

export class CompanySuggestionItem {
  @IsString()
  id: string;

  @IsString()
  category: string;

  @IsString()
  original: string;

  @IsString()
  suggestion: string;

  @IsString()
  reason: string;

  @IsEnum(SeverityLevel)
  severity: SeverityLevel;
}

export class GrammarSection {
  @IsNumber()
  score: number;

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => CompanySuggestionItem)
  suggestions: CompanySuggestionItem[];
}

export class ProtocolSection {
  @IsNumber()
  score: number;

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => CompanySuggestionItem)
  suggestions: CompanySuggestionItem[];
}

export class CompanyAnalysis {
  @IsString()
  companyId: string;

  @IsString()
  communicationStyle: string;

  @IsNumber()
  complianceLevel: number;

  @IsString()
  methodUsed: string;

  @IsNumber()
  processingTime: number;

  @IsInt()
  ragSourcesCount: number;
}

export class CompanyQualityAnalysisResponseDto {
  @IsNumber()
  grammarScore: number;

  @IsNumber()
  formalityScore: number;

  @IsNumber()
  readabilityScore: number;

  @IsNumber()
  protocolScore: number;

  @IsNumber()
  complianceScore: number;

  @IsObject()
  @ValidateNested()
  @Type(() => GrammarSection)
  grammarSection: GrammarSection;

  @IsObject()
  @ValidateNested()
  @Type(() => ProtocolSection)
  protocolSection: ProtocolSection;

  @IsObject()
  @ValidateNested()
  @Type(() => CompanyAnalysis)
  companyAnalysis: CompanyAnalysis;
}
