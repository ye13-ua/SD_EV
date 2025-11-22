import { UUID } from "node:crypto";
import { IsNumber, IsString, IsUUID, Min } from "class-validator";

export class CreateCpsDto {
    @IsUUID()
    ID: String;

    @IsString()
    Ciudad: String;

    @IsString()
    Calle: String;

    @IsNumber()
    @Min(0)
    Precio_KWH: number;

}

export class UpdateCpsDto {
    @IsUUID()
    ID: String;

    @IsString()
    Ciudad?: String;

    @IsString()
    Calle?: String;

    @IsNumber()
    @Min(0)
    Precio_KWH?: number;

}

export class PushCpsDto {
    
}