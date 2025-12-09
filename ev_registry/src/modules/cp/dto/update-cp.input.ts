
import { Field, InputType, PartialType } from "@nestjs/graphql";
import { IsUUID } from "class-validator";
import { CreateCpDto } from "./create-cp.input";

@InputType()
export class UpdateCpDto extends PartialType(CreateCpDto) {
   
    @Field()
    @IsUUID()
    id: string
}