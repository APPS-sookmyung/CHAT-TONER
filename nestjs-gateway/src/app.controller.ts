import { Body, Controller, HttpException, HttpStatus, Post, Get } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { ConversionRequestDto } from './dto/conversion-request.dto';
import { ConversionResponseDto } from './dto/conversion-response.dto';
import { FeedbackRequestDto } from './dto/feedback-request.dto';
import { FeedbackResponseDto } from './dto/feedback-response.dto';
import { firstValueFrom } from 'rxjs';
import { AxiosError } from 'axios';
import { FinetuneRequestDto } from './dto/finetune-request.dto';
import { FinetuneResponseDto } from './dto/finetune-response.dto';

@Controller('api')
export class AppController {
  constructor(private readonly httpService: HttpService) {}

  @Get()
  getRoot(): string {
    return '서버가 정상 작동 중입니다!';
  }

  @Post('conversion/convert')
  async convertText(
    @Body() body: ConversionRequestDto,
  ): Promise<ConversionResponseDto> {
    try {
      const fastApiUrl = 'http://127.0.0.1:5001/api/v1/conversion/convert';
      const response = await firstValueFrom(
        this.httpService.post(fastApiUrl, body),
      );
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError && error.response) {
        throw new HttpException(
          error.response.data,
          error.response.status,
        );
      }
      throw new HttpException(
        '텍스트 변환 중 오류 발생',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Post('finetune/convert')
  async finetuneConvert(
    @Body() body: FinetuneRequestDto,
  ): Promise<FinetuneResponseDto> {
    try {
      const fastApiUrl = 'http://127.0.0.1:5001/api/v1/finetune/convert';
      const response = await firstValueFrom(
        this.httpService.post(fastApiUrl, body),
      );
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError && error.response) {
        throw new HttpException(
          error.response.data,
          error.response.status,
        );
      }
      throw new HttpException(
        '파인튜닝 변환 중 오류 발생',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Post('feedback')
  async submitFeedback(
    @Body() body: FeedbackRequestDto,
  ): Promise<FeedbackResponseDto> {
    try {
      // 💡 여기에 피드백 저장 또는 전송 로직 연결 예정
      return {
        success: true,
        message: '피드백이 반영되었습니다.',
        data: {
          received_feedback: body.feedback_text,
        },
      };
    } catch (e) {
      throw new HttpException(
        '피드백 처리 중 오류 발생',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }
}
