import { ApiProperty } from '@nestjs/swagger';
import { IsString, IsBoolean, IsInt, IsOptional } from 'class-validator';

export class RAGIngestRequestDto {
  @ApiProperty({
    description: 'The path to the folder containing documents to ingest.',
    default: 'python_backend/langchain_pipeline/data/documents',
  })
  @IsString()
  folder_path: string;
}

export class RAGIngestResponseDto {
  @ApiProperty()
  @IsBoolean()
  success: boolean;

  @ApiProperty()
  @IsInt()
  documents_processed: number;

  @ApiProperty()
  @IsString()
  message: string;

  @ApiProperty({ required: false })
  @IsString()
  @IsOptional()
  error?: string;
}
