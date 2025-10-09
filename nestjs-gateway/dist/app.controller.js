"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
var __param = (this && this.__param) || function (paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AppController = void 0;
const common_1 = require("@nestjs/common");
const axios_1 = require("@nestjs/axios");
const conversion_request_dto_1 = require("./dto/conversion-request.dto");
const feedback_request_dto_1 = require("./dto/feedback-request.dto");
const feedback_response_dto_1 = require("./dto/feedback-response.dto");
const rxjs_1 = require("rxjs");
const axios_2 = require("axios");
const quality_analysis_request_dto_1 = require("./dto/quality-analysis-request.dto");
const rag_query_dto_1 = require("./dto/rag-query.dto");
const rag_ingest_dto_1 = require("./dto/rag-ingest.dto");
const profile_dto_1 = require("./dto/profile.dto");
let AppController = class AppController {
    httpService;
    fastApiBaseUrl;
    constructor(httpService) {
        this.httpService = httpService;
        this.fastApiBaseUrl =
            process.env.BACKEND_API_URL || 'http://127.0.0.1:5001';
    }
    getRoot() {
        return '서버가 정상 작동 중입니다!';
    }
    async convertText(body) {
        try {
            const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/conversion/convert`;
            const response = await (0, rxjs_1.firstValueFrom)(this.httpService.post(fastApiUrl, body));
            return response.data;
        }
        catch (error) {
            if (error instanceof axios_2.AxiosError && error.response) {
                throw new common_1.HttpException(error.response.data, error.response.status);
            }
            throw new common_1.HttpException('텍스트 변환 중 오류 발생', common_1.HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }
    async analyzeCompanyTextQuality(body) {
        try {
            const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/quality/company/analyze`;
            const response = await (0, rxjs_1.firstValueFrom)(this.httpService.post(fastApiUrl, body));
            return response.data;
        }
        catch (error) {
            if (error instanceof axios_2.AxiosError && error.response) {
                throw new common_1.HttpException(error.response.data, error.response.status);
            }
            throw new common_1.HttpException('기업용 품질 분석 중 오류 발생', common_1.HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }
    async askRagQuestion(body) {
        try {
            const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/rag/ask`;
            const response = await (0, rxjs_1.firstValueFrom)(this.httpService.post(fastApiUrl, body));
            return response.data;
        }
        catch (error) {
            if (error instanceof axios_2.AxiosError && error.response) {
                throw new common_1.HttpException(error.response.data, error.response.status);
            }
            throw new common_1.HttpException('RAG 질의응답 중 오류 발생', common_1.HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }
    async ingestRagDocuments(body) {
        try {
            const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/rag/ingest`;
            const response = await (0, rxjs_1.firstValueFrom)(this.httpService.post(fastApiUrl, body));
            return response.data;
        }
        catch (error) {
            if (error instanceof axios_2.AxiosError && error.response) {
                throw new common_1.HttpException(error.response.data, error.response.status);
            }
            throw new common_1.HttpException('RAG 문서 주입 중 오류 발생', common_1.HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }
    async getUserProfile(userId) {
        try {
            const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/profile/${userId}`;
            const response = await (0, rxjs_1.firstValueFrom)(this.httpService.get(fastApiUrl));
            return response.data;
        }
        catch (error) {
            if (error instanceof axios_2.AxiosError && error.response) {
                throw new common_1.HttpException(error.response.data, error.response.status);
            }
            throw new common_1.HttpException('사용자 프로필 조회 중 오류 발생', common_1.HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }
    async saveUserProfile(body) {
        try {
            const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/profile`;
            const response = await (0, rxjs_1.firstValueFrom)(this.httpService.post(fastApiUrl, body));
            return response.data;
        }
        catch (error) {
            if (error instanceof axios_2.AxiosError && error.response) {
                throw new common_1.HttpException(error.response.data, error.response.status);
            }
            throw new common_1.HttpException('사용자 프로필 저장 중 오류 발생', common_1.HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }
    submitFeedback(body) {
        try {
            return {
                success: true,
                message: '피드백이 반영되었습니다.',
                data: {
                    received_feedback: body.feedback_text,
                },
            };
        }
        catch {
            throw new common_1.HttpException('피드백 처리 중 오류 발생', common_1.HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }
};
exports.AppController = AppController;
__decorate([
    (0, common_1.Get)(),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", String)
], AppController.prototype, "getRoot", null);
__decorate([
    (0, common_1.Post)('conversion/convert'),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [conversion_request_dto_1.ConversionRequestDto]),
    __metadata("design:returntype", Promise)
], AppController.prototype, "convertText", null);
__decorate([
    (0, common_1.Post)('quality/company/analyze'),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [quality_analysis_request_dto_1.CompanyQualityAnalysisRequestDto]),
    __metadata("design:returntype", Promise)
], AppController.prototype, "analyzeCompanyTextQuality", null);
__decorate([
    (0, common_1.Post)('rag/ask'),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [rag_query_dto_1.RAGQueryRequestDto]),
    __metadata("design:returntype", Promise)
], AppController.prototype, "askRagQuestion", null);
__decorate([
    (0, common_1.Post)('rag/ingest'),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [rag_ingest_dto_1.RAGIngestRequestDto]),
    __metadata("design:returntype", Promise)
], AppController.prototype, "ingestRagDocuments", null);
__decorate([
    (0, common_1.Get)('profile/:user_id'),
    __param(0, (0, common_1.Param)('user_id')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", Promise)
], AppController.prototype, "getUserProfile", null);
__decorate([
    (0, common_1.Post)('profile'),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [profile_dto_1.ProfileRequestDto]),
    __metadata("design:returntype", Promise)
], AppController.prototype, "saveUserProfile", null);
__decorate([
    (0, common_1.Post)('feedback'),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [feedback_request_dto_1.FeedbackRequestDto]),
    __metadata("design:returntype", feedback_response_dto_1.FeedbackResponseDto)
], AppController.prototype, "submitFeedback", null);
exports.AppController = AppController = __decorate([
    (0, common_1.Controller)('api/v1'),
    __metadata("design:paramtypes", [axios_1.HttpService])
], AppController);
//# sourceMappingURL=app.controller.js.map