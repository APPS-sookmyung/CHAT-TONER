import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
  HttpException,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Request } from 'express';
import { AxiosError } from 'axios';
import { ErrorResponseDto } from '../dto/error-response.dto';

@Injectable()
export class ErrorInterceptor implements NestInterceptor {
  private readonly logger = new Logger(ErrorInterceptor.name);

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const request = context.switchToHttp().getRequest<Request>();

    return next.handle().pipe(
      catchError((error) => {
        const errorResponse = this.buildErrorResponse(error, request);

        // Log error with appropriate level
        this.logError(error, request, errorResponse);

        // Throw the standardized error
        throw new HttpException(errorResponse, errorResponse.statusCode);
      }),
    );
  }

  private buildErrorResponse(error: any, request: Request): ErrorResponseDto {
    const timestamp = new Date().toISOString();
    const path = request.url;

    // Handle HttpException (including those thrown from controllers)
    if (error instanceof HttpException) {
      const status = error.getStatus();
      const response = error.getResponse();

      // If response is already structured, preserve it
      if (typeof response === 'object' && 'statusCode' in response) {
        return {
          statusCode: status,
          message: (response as any).message || error.message,
          error: (response as any).error || this.getErrorName(status),
          timestamp,
          path,
          details: (response as any).details,
        };
      }

      // If response is a string or simple object, structure it
      return {
        statusCode: status,
        message: typeof response === 'string' ? response : error.message,
        error: this.getErrorName(status),
        timestamp,
        path,
        details: typeof response === 'object' ? response : undefined,
      };
    }

    // Handle AxiosError (errors from FastAPI backend)
    if (error instanceof AxiosError) {
      const status = error.response?.status || HttpStatus.INTERNAL_SERVER_ERROR;
      const backendError = error.response?.data;

      return {
        statusCode: status,
        message: this.extractMessage(backendError) || error.message,
        error: this.getErrorName(status),
        timestamp,
        path,
        details: typeof backendError === 'object' ? backendError : undefined,
      };
    }

    // Handle unexpected errors
    return {
      statusCode: HttpStatus.INTERNAL_SERVER_ERROR,
      message: error.message || 'Internal server error',
      error: 'Internal Server Error',
      timestamp,
      path,
    };
  }

  private extractMessage(errorData: any): string | undefined {
    if (!errorData) return undefined;
    if (typeof errorData === 'string') return errorData;
    if (typeof errorData === 'object') {
      return errorData.message || errorData.detail || errorData.error;
    }
    return undefined;
  }

  private getErrorName(statusCode: number): string {
    const errorNames: Record<number, string> = {
      400: 'Bad Request',
      401: 'Unauthorized',
      403: 'Forbidden',
      404: 'Not Found',
      422: 'Unprocessable Entity',
      500: 'Internal Server Error',
      502: 'Bad Gateway',
      503: 'Service Unavailable',
    };
    return errorNames[statusCode] || 'Error';
  }

  private sanitizeDetails(details: any): any {
    // For client errors (4xx), avoid logging potentially sensitive request bodies.
    if (details) {
      return { message: 'Details sanitized for client error' };
    }
    return details;
  }

  private safeStringify(obj: any): string {
    const cache = new Set();
    return JSON.stringify(obj, (key, value) => {
      if (typeof value === 'object' && value !== null) {
        if (cache.has(value)) {
          // Circular reference found, replace with a placeholder
          return '[Circular]';
        }
        // Store value in our collection
        cache.add(value);
      }
      return value;
    });
  }

  private logError(error: any, request: Request, errorResponse: ErrorResponseDto): void {
    const { statusCode, message, details } = errorResponse;
    const { method, url } = request;

    // Log context
    const logContext = {
      method,
      url,
      statusCode,
      message,
      details: statusCode >= 500 ? details : this.sanitizeDetails(details),
    };

    // Log with appropriate level based on status code
    if (statusCode >= 500) {
      this.logger.error(
        `Server error on ${method} ${url}: ${message}`,
        error.stack, // Include stack trace for server errors
      );
    } else {
      this.logger.warn(
        `Client error on ${method} ${url}: ${message}`,
        this.safeStringify(logContext), // Use safe stringify for context
      );
    }
  }
}
