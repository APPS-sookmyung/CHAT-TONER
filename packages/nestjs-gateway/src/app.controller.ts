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
import { AxiosError } from 'axios';
//@JiiminHa
// import { FinetuneRequestDto } from './dto/finetune-request.dto';
// import { FinetuneResponseDto } from './dto/finetune-response.dto';
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
    try {
      const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/conversion/convert`;
      const response = await firstValueFrom(
        this.httpService.post(fastApiUrl, body),
      );
      return response.data as ConversionResponseDto;
    } catch (error) {
      if (error instanceof AxiosError && error.response) {
        throw new HttpException(
          error.response.data as string | Record<string, any>,
          error.response.status,
        );
      }
      throw new HttpException(
        '텍스트 변환 중 오류 발생',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  // Finetune route intentionally removed (not implemented on backend)

  @Get('quality/company/options')
  async getQualityCompanyOptions() {
    try {
      const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/quality/company/options`;
      const response = await firstValueFrom(
        this.httpService.get(fastApiUrl),
      );
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError && error.response) {
        throw new HttpException(error.response.data, error.response.status);
      }
      throw new HttpException(
        '옵션 조회 중 오류 발생',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Post('quality/company/analyze')
  async analyzeCompanyTextQuality(
    @Body() body: CompanyQualityAnalysisRequestDto,
  ): Promise<CompanyQualityAnalysisResponseDto> {
    try {
      const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/quality/company/analyze`;
      const response = await firstValueFrom(
        this.httpService.post<CompanyQualityAnalysisResponseDto>(
          fastApiUrl,
          body,
        ),
      );
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError && error.response) {
        throw new HttpException(error.response.data, error.response.status);
      }
      throw new HttpException(
        '기업용 품질 분석 중 오류 발생',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Post('rag/ask')
  async askRagQuestion(
    @Body() body: RAGQueryRequestDto,
  ): Promise<RAGQueryResponseDto> {
    try {
      const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/rag/ask`;
      const response = await firstValueFrom(
        this.httpService.post<RAGQueryResponseDto>(fastApiUrl, body),
      );
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError && error.response) {
        throw new HttpException(error.response.data, error.response.status);
      }
      throw new HttpException(
        'RAG 질의응답 중 오류 발생',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Post('rag/ingest')
  async ingestRagDocuments(
    @Body() body: RAGIngestRequestDto,
  ): Promise<RAGIngestResponseDto> {
    try {
      const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/rag/ingest`;
      const response = await firstValueFrom(
        this.httpService.post<RAGIngestResponseDto>(fastApiUrl, body),
      );
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError && error.response) {
        throw new HttpException(error.response.data, error.response.status);
      }
      throw new HttpException(
        'RAG 문서 주입 중 오류 발생',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Get('profile/:user_id')
  async getUserProfile(
    @Param('user_id') userId: string,
  ): Promise<ProfileResponseDto> {
    try {
      const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/profile/${userId}`;
      const response = await firstValueFrom(
        this.httpService.get<ProfileResponseDto>(fastApiUrl),
      );
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError && error.response) {
        throw new HttpException(error.response.data, error.response.status);
      }
      throw new HttpException(
        '사용자 프로필 조회 중 오류 발생',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Post('profile')
  async saveUserProfile(
    @Body() body: ProfileRequestDto,
  ): Promise<ProfileResponseDto> {
    try {
      const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/profile`;
      const response = await firstValueFrom(
        this.httpService.post<ProfileResponseDto>(fastApiUrl, body),
      );
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError && error.response) {
        throw new HttpException(error.response.data, error.response.status);
      }
      throw new HttpException(
        '사용자 프로필 저장 중 오류 발생',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Post('feedback')
  submitFeedback(@Body() body: FeedbackRequestDto): FeedbackResponseDto {
    try {
      // TODO: 피드백 저장소 연결 및 실제 피드백 처리 로직 구현 필요
      // Feedback storage or transmission logic connection planned
      return {
        success: true,
        message: '피드백이 반영되었습니다.',
        data: {
          received_feedback: body.feedback_text,
        },
      };
    } catch {
      throw new HttpException(
        '피드백 처리 중 오류 발생',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }
}
