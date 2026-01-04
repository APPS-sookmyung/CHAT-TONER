import { ApiProperty } from '@nestjs/swagger';

export class ErrorResponseDto {
  @ApiProperty({
    description: 'HTTP status code',
    example: 500,
  })
  statusCode: number;

  @ApiProperty({
    description: 'Error message',
    example: 'Internal Server Error',
  })
  message: string;

  @ApiProperty({
    description: 'Error type',
    example: 'Internal Server Error',
  })
  error: string;

  @ApiProperty({
    description: 'Timestamp of the error',
    example: '2026-01-03T10:30:00.000Z',
  })
  timestamp: string;

  @ApiProperty({
    description: 'Request path',
    example: '/api/v1/conversion/convert',
  })
  path: string;

  @ApiProperty({
    description: 'Additional error details',
    required: false,
  })
  details?: any;
}
