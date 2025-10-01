import { IsString, IsBoolean, IsOptional, IsObject, IsArray, ValidateNested, IsNotEmpty, IsNumber } from 'class-validator';
import { Type } from 'class-transformer';

// Based on python_backend/api/v1/schemas/conversion.py UserProfile
class UserProfileDto {
  @IsOptional()
  @IsString()
  jobRole?: string;

  @IsOptional()
  @IsString()
  department?: string;

  @IsOptional()
  @IsString()
  company?: string;

  @IsOptional()
  @IsNumber()
  baseFormalityLevel?: number;

  @IsOptional()
  @IsNumber()
  baseFriendlinessLevel?: number;
}

export class RAGQueryRequestDto {
  @IsString()
  @IsNotEmpty()
  query: string;

  @IsOptional()
  @IsString()
  context?: string;

  @IsOptional()
  @IsBoolean()
  use_styles?: boolean;

  @IsOptional()
  @IsObject()
  @ValidateNested()
  @Type(() => UserProfileDto)
  user_profile?: UserProfileDto;
}

class SourceDto {
  @IsString()
  source: string;

  @IsString()
  content: string;
}

export class RAGQueryResponseDto {
  @IsBoolean()
  success: boolean;

  @IsOptional()
  @IsString()
  answer?: string;

  @IsOptional()
  @IsObject()
  converted_texts?: Record<string, string>;

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => SourceDto)
  sources: SourceDto[];

  @IsOptional()
  @IsString()
  rag_context?: string;

  @IsOptional()
  @IsString()
  error?: string;

  @IsObject()
  metadata: Record<string, any>;
}
