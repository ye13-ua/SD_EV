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
    
    @Field()
    @Length(3, 60)
    @IsString()
    calle: string
    
    @Field(() => Float)
    @IsNumber()
    @Min(0)
    precio_kwh: number

    // ----------------------- REGISTRO -----------------------
    @Field({nullable: true})
    clientId: string
    
    @Field({nullable: true})
    clientSecretHash: string

    // ----------------------- AUTENTICACIÓN -----------------------
    @Field({nullable: true})
    symmetricKey: string
}