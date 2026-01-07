
import { Field, InputType, PartialType } from "@nestjs/graphql";
import {IsUUID} from "class-validator";

type CPType = "ACTIVE" | "WAITING" | "OUT_OF_SERVICE" | "CHARGING_CENTRAL" | "BROKEN" | "DISCONNECTED" | "FINISHED_CHARGING" | "COLD";

@InputType()
export class StatusCpInput {
   
    @Field()
    @IsUUID()
    id: string
    
    @Field()
    iv: string

    @Field()
    ciphertext: string

    @Field()
    tag: string


    /*
    // ACTIVE - WAITING - OUT_OF_SERVICE - CHARGING_CENTRAL - BROKEN - DISCONNECTED |!| FINISHED_CHARGING
    @Field({nullable: true})     
    @IsString()
    estado: CPType

    @Field({nullable: true})
    @IsBoolean()
    isChanged: boolean

    @Field({nullable: true})
    @Min(0)
    timeStamp: number;

    @Field({nullable: true})
    @IsBoolean()
    kafkaOK: boolean
    
    @Field({nullable: true})
    @IsNumber()
    @Min(0)
    alreadyCharged: number

    @Field({nullable: true})
    @IsUUID()
    driverId: string


    //IF -> FINISHED_CHARGING
    @Field({nullable: true})
    @IsNumber()
    @Min(0)
    price: number
    */
}