import { Field, Float, InputType } from "@nestjs/graphql";
import { IsHash, IsNumber, IsString, IsUUID, Length, Min } from "class-validator";

@InputType()
export class CreateCpInput {

    @Field()
    @IsUUID()
    id: string

    @Field()
    @IsString()
    ciudad: string
    
    @Field(() => Float)
    @IsNumber()
    @Min(0)
    precio_kwh: number

    // ----------------------- REGISTRO -----------------------
    @Field({nullable: true})
    clientSecret: string
z
}