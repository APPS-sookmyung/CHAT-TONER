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
import { ProfileRequestDto, ProfileResponseDto } from './dto/profile.dto';

@Controller('api')
export class AppController {
  private readonly fastApiBaseUrl: string;

  constructor(private readonly httpService: HttpService) {
    this.fastApiBaseUrl =
      process.env.BACKEND_API_URL || 'http://127.0.0.1:5001';
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

  // @Post('finetune/convert')
  // async finetuneConvert(
  //   @Body() body: FinetuneRequestDto,
  // ): Promise<FinetuneResponseDto> {
  //   try {
  //     const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/finetune/convert`;
  //     const response = await firstValueFrom(
  //       this.httpService.post(fastApiUrl, body),
  //     );
  //     return response.data;
  //   } catch (error) {
  //     if (error instanceof AxiosError && error.response) {
  //       throw new HttpException(
  //         error.response.data,
  //         error.response.status,
  //       );
  //     }
  //     throw new HttpException(
  //       '파인튜닝 변환 중 오류 발생',
  //       HttpStatus.INTERNAL_SERVER_ERROR,
  //     );
  //   }
  // }

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
