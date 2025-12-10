import { Field, Float, InputType } from "@nestjs/graphql";
import { IsNumber, IsString, IsUUID, Length, Min } from "class-validator";

@InputType()
export class CreateCpInput {

    @Field()
    @IsUUID()
    id: string

    @Field()
    @IsString()
    ciudad: string
    
    @Field()
    @Length(3, 30)
    @IsString()
    calle: string
    
    @Field(() => Float)
    @IsNumber()
    @Min(0)
    precio_kwh: number
}