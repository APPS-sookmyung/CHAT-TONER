// nestjs-gateway/src/dto/finetune-request.dto.ts
import { IsString, IsOptional, IsObject, IsBoolean } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class FinetuneRequestDto {
    @ApiProperty({ description: '변환할 원본 텍스트' })
    @IsString()
    text: string;

    @ApiProperty({ description: '사용자 프로필 정보' })
    @IsObject()
    user_profile: Record<string, any>;

    @ApiPropertyOptional({ description: '텍스트가 사용되는 맥락 (선택사항)' })
    @IsOptional()
    @IsString()
    context?: string;

    @ApiPropertyOptional({ description: '강제 변환 여부 (선택사항)' })
    @IsOptional()
    @IsBoolean()
    force_convert?: boolean;
}
