import {
  Body,
  Controller,
  HttpException,
  HttpStatus,
  Post,
  Get,
  Param,
  Delete,
  Query,
  UploadedFiles,
  UseInterceptors,
} from '@nestjs/common';
import { FileFieldsInterceptor } from '@nestjs/platform-express';
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

  // ========== Documents Endpoints ==========

  @Post('documents/upload')
  @UseInterceptors(FileFieldsInterceptor([{ name: 'files', maxCount: 10 }]))
  async uploadDocuments(
    @UploadedFiles() files: { files?: any[] },
    @Body() body: any,
  ) {
    const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/documents/upload`;
    const FormData = require('form-data');
    const formData = new FormData();

    if (files?.files) {
      for (const file of files.files) {
        formData.append('files', file.buffer, {
          filename: file.originalname,
          contentType: file.mimetype,
        });
      }
    }

    if (body.subdir) {
      formData.append('subdir', body.subdir);
    }

    const response = await firstValueFrom(
      this.httpService.post(fastApiUrl, formData, {
        headers: formData.getHeaders(),
      }),
    );
    return response.data;
  }

  @Get('documents')
  async listDocuments(@Query('subdir') subdir?: string) {
    const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/documents/`;
    const response = await firstValueFrom(
      this.httpService.get(fastApiUrl, {
        params: subdir ? { subdir } : {},
      }),
    );
    return response.data;
  }

  @Delete('documents/:documentName')
  async deleteDocument(@Param('documentName') documentName: string) {
    const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/documents/${encodeURIComponent(documentName)}`;
    const response = await firstValueFrom(
      this.httpService.delete(fastApiUrl),
    );
    return response.data;
  }

  @Post('documents/summarize-pdf')
  async summarizePDF(
    @Body() body: { document_name: string; summary_type: string },
  ) {
    const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/documents/summarize-pdf`;
    const response = await firstValueFrom(
      this.httpService.post(fastApiUrl, body),
    );
    return response.data;
  }

  @Post('documents/summarize-text')
  async summarizeText(
    @Body() body: { text: string; summary_type: string },
  ) {
    const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/documents/summarize-text`;
    const response = await firstValueFrom(
      this.httpService.post(fastApiUrl, body),
    );
    return response.data;
  }

  // ========== Surveys Endpoints ==========

  @Get('surveys/:key')
  async getSurvey(@Param('key') key: string) {
    const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/surveys/${key}`;
    const response = await firstValueFrom(
      this.httpService.get(fastApiUrl),
    );
    return response.data;
  }

  @Post('surveys/:key/responses')
  async submitSurveyResponse(
    @Param('key') key: string,
    @Body() body: { tenant_id: string; user_id: string; answers: Record<string, any> },
  ) {
    const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/surveys/${key}/responses`;
    const response = await firstValueFrom(
      this.httpService.post(fastApiUrl, body),
    );
    return response.data;
  }

  // ========== Additional Quality Endpoints ==========

  @Get('quality/company/:companyId/status')
  async getCompanyStatus(@Param('companyId') companyId: string) {
    const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/quality/company/${companyId}/status`;
    const response = await firstValueFrom(
      this.httpService.get(fastApiUrl),
    );
    return response.data;
  }

  @Post('quality/company/test-setup')
  async createTestCompany(@Body() body: { company_id: string }) {
    const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/quality/company/test-setup`;
    const response = await firstValueFrom(
      this.httpService.post(fastApiUrl, body),
    );
    return response.data;
  }

  @Post('quality/company/generate-final')
  async generateFinalText(@Body() body: any) {
    const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/quality/company/generate-final`;
    const response = await firstValueFrom(
      this.httpService.post(fastApiUrl, body),
    );
    return response.data;
  }
}
