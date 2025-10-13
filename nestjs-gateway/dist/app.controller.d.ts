import { HttpService } from '@nestjs/axios';
import { ConversionRequestDto } from './dto/conversion-request.dto';
import { ConversionResponseDto } from './dto/conversion-response.dto';
import { FeedbackRequestDto } from './dto/feedback-request.dto';
import { FeedbackResponseDto } from './dto/feedback-response.dto';
import { CompanyQualityAnalysisRequestDto } from './dto/quality-analysis-request.dto';
import { CompanyQualityAnalysisResponseDto } from './dto/quality-analysis-response.dto';
import { RAGQueryRequestDto, RAGQueryResponseDto } from './dto/rag-query.dto';
import { RAGIngestRequestDto, RAGIngestResponseDto } from './dto/rag-ingest.dto';
import { ProfileRequestDto, ProfileResponseDto } from './dto/profile.dto';
export declare class AppController {
    private readonly httpService;
    private readonly fastApiBaseUrl;
    constructor(httpService: HttpService);
    getRoot(): string;
    convertText(body: ConversionRequestDto): Promise<ConversionResponseDto>;
    analyzeCompanyTextQuality(body: CompanyQualityAnalysisRequestDto): Promise<CompanyQualityAnalysisResponseDto>;
    askRagQuestion(body: RAGQueryRequestDto): Promise<RAGQueryResponseDto>;
    ingestRagDocuments(body: RAGIngestRequestDto): Promise<RAGIngestResponseDto>;
    getUserProfile(userId: string): Promise<ProfileResponseDto>;
    saveUserProfile(body: ProfileRequestDto): Promise<ProfileResponseDto>;
    submitFeedback(body: FeedbackRequestDto): FeedbackResponseDto;
}
