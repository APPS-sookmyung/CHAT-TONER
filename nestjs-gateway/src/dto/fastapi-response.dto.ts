// nestjs-gateway/src/dto/fastapi-response.dto.ts
import { IsString, IsNumber, IsArray } from 'class-validator';

export class FastApiResponseDto {
  @IsString()
  answer!: string;

  @IsArray()
  sources!: string[]; // Source document URLs or titles

  @IsNumber()
  confidence!: number; // e.g., 0.87 (confidence level)
}
