// nestjs-gateway/src/dto/finetune-response.dto.ts
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class FinetuneResponseDto {
    @ApiProperty({ description: '성공 여부' })
    success: boolean;

    @ApiPropertyOptional({ description: '변환된 텍스트' })
    converted_text?: string;

    @ApiPropertyOptional({ description: 'LoRA 모델 출력' })
    lora_output?: string;

    @ApiProperty({ description: '사용된 변환 방법' })
    method: string;

    @ApiProperty({ description: '변환 결정 이유' })
    reason: string;

    @ApiPropertyOptional({ description: '강제 변환 여부' })
    forced?: boolean;

    @ApiPropertyOptional({ description: '에러 메시지' })
    error?: string;

    @ApiPropertyOptional({ description: '메타데이터' })
    metadata?: Record<string, any>;

    @ApiPropertyOptional({ description: '타임스탬프' })
    timestamp?: string;
}
