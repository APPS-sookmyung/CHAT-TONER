# Error Handling in NestJS Gateway

This document describes the standardized error handling implemented in the NestJS Gateway.

## Overview

The gateway now uses a centralized error handling approach using NestJS interceptors. This eliminates code duplication and ensures consistent error responses across all endpoints.

## Architecture

### Components

1. **ErrorInterceptor** (`src/interceptors/error.interceptor.ts`)
   - Global error interceptor that catches all errors
   - Transforms errors into standardized format
   - Logs errors with appropriate levels

2. **LoggingInterceptor** (`src/interceptors/logging.interceptor.ts`)
   - Logs all incoming requests and responses
   - Tracks request duration
   - Provides request/response visibility

3. **ErrorResponseDto** (`src/dto/error-response.dto.ts`)
   - Standardized error response structure
   - Documented with Swagger decorators

### Error Response Format

All errors are returned in the following standardized format:

```typescript
{
  "statusCode": number,      // HTTP status code (e.g., 400, 500)
  "message": string,          // Human-readable error message
  "error": string,            // Error type (e.g., "Bad Request", "Internal Server Error")
  "timestamp": string,        // ISO 8601 timestamp
  "path": string,             // Request path that caused the error
  "details": any              // Optional additional error details (from backend)
}
```

### Error Flow

1. Request comes into controller
2. LoggingInterceptor logs the request
3. Controller executes business logic
4. If error occurs:
   - ErrorInterceptor catches it
   - Error is transformed to ErrorResponseDto
   - Error is logged with appropriate level
   - Standardized error response is returned
5. LoggingInterceptor logs the response

## Error Types Handled

### 1. HttpException
Errors explicitly thrown by controllers (e.g., validation errors, business logic errors)

```typescript
throw new HttpException('Custom error message', HttpStatus.BAD_REQUEST);
```

### 2. AxiosError
Errors from FastAPI backend when proxy calls fail

- Status code and message are preserved from backend
- Backend error details are included in `details` field
- Handles both string and object error responses

### 3. Unexpected Errors
Any other unhandled errors

- Returns 500 Internal Server Error
- Error message is extracted when available
- Stack trace is logged for debugging

## Logging Levels

The ErrorInterceptor automatically determines log level based on status code:

- **ERROR** (statusCode >= 500): Server errors with stack trace
- **WARN** (400 <= statusCode < 500): Client errors with context
- **LOG** (statusCode < 400): Informational errors

## Usage in Controllers

Controllers no longer need try-catch blocks for error handling. Simply write business logic:

### Before
```typescript
@Post('conversion/convert')
async convertText(@Body() body: ConversionRequestDto): Promise<ConversionResponseDto> {
  try {
    const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/conversion/convert`;
    const response = await firstValueFrom(this.httpService.post(fastApiUrl, body));
    return response.data as ConversionResponseDto;
  } catch (error) {
    if (error instanceof AxiosError && error.response) {
      throw new HttpException(error.response.data, error.response.status);
    }
    throw new HttpException('텍스트 변환 중 오류 발생', HttpStatus.INTERNAL_SERVER_ERROR);
  }
}
```

### After
```typescript
@Post('conversion/convert')
async convertText(@Body() body: ConversionRequestDto): Promise<ConversionResponseDto> {
  const fastApiUrl = `${this.fastApiBaseUrl}/api/v1/conversion/convert`;
  const response = await firstValueFrom(this.httpService.post(fastApiUrl, body));
  return response.data as ConversionResponseDto;
}
```

The interceptor automatically handles all errors and returns standardized responses.

## Example Error Responses

### Validation Error (400)
```json
{
  "statusCode": 400,
  "message": "Validation failed",
  "error": "Bad Request",
  "timestamp": "2026-01-03T10:30:00.000Z",
  "path": "/api/v1/conversion/convert",
  "details": {
    "field": "text",
    "constraint": "text should not be empty"
  }
}
```

### Backend Error (from FastAPI)
```json
{
  "statusCode": 422,
  "message": "Invalid tone parameter",
  "error": "Unprocessable Entity",
  "timestamp": "2026-01-03T10:30:00.000Z",
  "path": "/api/v1/conversion/convert",
  "details": {
    "detail": "tone must be one of: formal, casual, friendly"
  }
}
```

### Server Error (500)
```json
{
  "statusCode": 500,
  "message": "Internal server error",
  "error": "Internal Server Error",
  "timestamp": "2026-01-03T10:30:00.000Z",
  "path": "/api/v1/conversion/convert"
}
```

## Benefits

1. **Consistency**: All errors follow the same format
2. **Reduced Duplication**: No more repetitive try-catch blocks
3. **Better Logging**: Automatic logging with appropriate levels
4. **Maintainability**: Single source of truth for error handling
5. **Debugging**: Detailed error information preserved
6. **API Stability**: HTTP status codes and error messages preserved from backend

## Configuration

The interceptors are registered globally in `app.module.ts`:

```typescript
{
  provide: APP_INTERCEPTOR,
  useClass: LoggingInterceptor,
},
{
  provide: APP_INTERCEPTOR,
  useClass: ErrorInterceptor,
}
```

Order matters: LoggingInterceptor runs first to capture all requests, ErrorInterceptor catches errors.

## Testing

To test error handling:

1. **Validation Error**: Send invalid request body
2. **Backend Error**: Trigger error from FastAPI backend
3. **Server Error**: Stop FastAPI backend and make request

All should return standardized error responses in the documented format.
