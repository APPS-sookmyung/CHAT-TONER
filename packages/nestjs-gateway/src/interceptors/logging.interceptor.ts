import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
  Logger,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { Request, Response } from 'express';

@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  private readonly logger = new Logger(LoggingInterceptor.name);

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const request = context.switchToHttp().getRequest<Request>();
    const response = context.switchToHttp().getResponse<Response>();
    const { method, url } = request;
    const startTime = Date.now();

    // Log incoming request
    this.logger.log(`Incoming ${method} ${url}`);

    return next.handle().pipe(
      tap({
        next: () => {
          const elapsedTime = Date.now() - startTime;
          const { statusCode } = response;
          this.logger.log(
            `Completed ${method} ${url} ${statusCode} - ${elapsedTime}ms`,
          );
        },
        error: (error) => {
          const elapsedTime = Date.now() - startTime;
          this.logger.error(
            `Failed ${method} ${url} - ${elapsedTime}ms`,
            error.stack,
          );
        },
      }),
    );
  }
}
