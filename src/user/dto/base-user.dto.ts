// src/users/dto/base-user.dto.ts
import { IsString, IsEmail, IsNotEmpty } from 'class-validator';

export class BaseUserDto {
    @IsString()
    @IsNotEmpty()
    name!: string;

    @IsEmail()
    @IsNotEmpty()
    email!: string;
}