// src/users/dto/create-user.dto.ts
import { IsString, MinLength } from 'class-validator';
import { BaseUserDto } from './base-user.dto';

export class CreateUserDto extends BaseUserDto {
    @IsString()
    @MinLength(8)
    readonly password!: string;
}