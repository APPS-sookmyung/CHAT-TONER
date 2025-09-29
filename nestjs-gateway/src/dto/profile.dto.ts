import { IsString, IsInt, IsOptional, IsObject, IsArray, Min, Max, IsNotEmpty } from 'class-validator';
import { Type } from 'class-transformer';

export class ProfileRequestDto {
  @IsString()
  @IsNotEmpty()
  userId: string;

  @IsInt()
  @Min(1)
  @Max(10)
  baseFormalityLevel: number = 5;

  @IsInt()
  @Min(1)
  @Max(10)
  baseFriendlinessLevel: number = 5;

  @IsInt()
  @Min(1)
  @Max(10)
  baseEmotionLevel: number = 5;

  @IsInt()
  @Min(1)
  @Max(10)
  baseDirectnessLevel: number = 5;

  @IsOptional()
  @IsInt()
  @Min(1)
  @Max(10)
  sessionFormalityLevel?: number;

  @IsOptional()
  @IsInt()
  @Min(1)
  @Max(10)
  sessionFriendlinessLevel?: number;

  @IsOptional()
  @IsInt()
  @Min(1)
  @Max(10)
  sessionEmotionLevel?: number;

  @IsOptional()
  @IsInt()
  @Min(1)
  @Max(10)
  sessionDirectnessLevel?: number;

  @IsOptional()
  @IsObject()
  responses?: Record<string, any>;
}

export class ProfileResponseDto {
  @IsInt()
  id: number;

  @IsString()
  userId: string;

  @IsInt()
  baseFormalityLevel: number;

  @IsInt()
  baseFriendlinessLevel: number;

  @IsInt()
  baseEmotionLevel: number;

  @IsInt()
  baseDirectnessLevel: number;

  @IsInt()
  sessionFormalityLevel: number;

  @IsInt()
  sessionFriendlinessLevel: number;

  @IsInt()
  sessionEmotionLevel: number;

  @IsInt()
  sessionDirectnessLevel: number;

  @IsObject()
  responses: Record<string, any>;

  @IsString()
  completedAt: string;

  @IsArray()
  @IsString({ each: true })
  negativePrompts: string[];
}
