import {
  Body,
  Controller,
  HttpException,
  HttpStatus,
  Post,
  Get,
  Param,
} from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { ConversionRequestDto } from './dto/conversion-request.dto';
import { ConversionResponseDto } from './dto/conversion-response.dto';
import { FeedbackRequestDto } from './dto/feedback-request.dto';
import { FeedbackResponseDto } from './dto/feedback-response.dto';
import { firstValueFrom } from 'rxjs';
import { CompanyQualityAnalysisRequestDto } from './dto/quality-analysis-request.dto';
import { CompanyQualityAnalysisResponseDto } from './dto/quality-analysis-response.dto';
import { RAGQueryRequestDto, RAGQueryResponseDto } from './dto/rag-query.dto';
import { RAGIngestRequestDto, RAGIngestResponseDto } from './dto/rag-ingest.dto';
import { ProfileRequestDto, ProfileResponseDto } from './dto/profile.dto';

@Controller('api/v1')
export class AppController {
  private readonly fastApiBaseUrl: string;

  constructor(private readonly httpService: HttpService) {
    this.fastApiBaseUrl =
      process.env.BACKEND_API_URL || 'http://127.0.0.1:8080';
    if (
      process.env.NODE_ENV === 'production' && !process.env.BACKEND_API_URL
    ) {
      throw new Error(
        'BACKEND_API_URL must be set in production for FastAPI proxying.',
      );
    }
  }

  @Get()
  getRoot(): string {
    return '서버가 정상 작동 중입니다!';
  }

  @Post('conversion/convert')
  async convertText(
    @Body() body: ConversionRequestDto,
  ): Promise<ConversionResponseDto> {
    const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/conversion/convert`;
    const response = await firstValueFrom(
      this.httpService.post(fastApiUrl, body),
    );
    return response.data as ConversionResponseDto;
  }

  // Finetune route intentionally removed (not implemented on backend)

  @Get('quality/company/options')
  async getQualityCompanyOptions() {
    const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/quality/company/options`;
    const response = await firstValueFrom(
      this.httpService.get(fastApiUrl),
    );
    return response.data;
  }

  @Post('quality/company/analyze')
  async analyzeCompanyTextQuality(
    @Body() body: CompanyQualityAnalysisRequestDto,
  ): Promise<CompanyQualityAnalysisResponseDto> {
    const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/quality/company/analyze`;
    const response = await firstValueFrom(
      this.httpService.post<CompanyQualityAnalysisResponseDto>(
        fastApiUrl,
        body,
      ),
    );
    return response.data;
  }

  @Post('rag/ask')
  async askRagQuestion(
    @Body() body: RAGQueryRequestDto,
  ): Promise<RAGQueryResponseDto> {
    const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/rag/ask`;
    const response = await firstValueFrom(
      this.httpService.post<RAGQueryResponseDto>(fastApiUrl, body),
    );
    return response.data;
  }

  @Post('rag/ingest')
  async ingestRagDocuments(
    @Body() body: RAGIngestRequestDto,
  ): Promise<RAGIngestResponseDto> {
    const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/rag/ingest`;
    const response = await firstValueFrom(
      this.httpService.post<RAGIngestResponseDto>(fastApiUrl, body),
    );
    return response.data;
  }

  @Get('profile/:user_id')
  async getUserProfile(
    @Param('user_id') userId: string,
  ): Promise<ProfileResponseDto> {
    const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/profile/${userId}`;
    const response = await firstValueFrom(
      this.httpService.get<ProfileResponseDto>(fastApiUrl),
    );
    return response.data;
  }

  @Post('profile')
  async saveUserProfile(
    @Body() body: ProfileRequestDto,
  ): Promise<ProfileResponseDto> {
    const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/profile`;
    const response = await firstValueFrom(
      this.httpService.post<ProfileResponseDto>(fastApiUrl, body),
    );
    return response.data;
  }

  @Post('feedback')
  submitFeedback(@Body() body: FeedbackRequestDto): FeedbackResponseDto {
    // TODO: 피드백 저장소 연결 및 실제 피드백 처리 로직 구현 필요
    // Feedback storage or transmission logic connection planned
    return {
      success: true,
      message: '피드백이 반영되었습니다.',
      data: {
        received_feedback: body.feedback_text,
      },
    };
  }
}
