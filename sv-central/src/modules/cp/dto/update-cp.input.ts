
import { Field, InputType, PartialType } from "@nestjs/graphql";
import { IsUUID } from "class-validator";
import { CreateCpInput } from "./create-cp.input";

@InputType()
export class UpdateCpInput extends PartialType(CreateCpInput) {
   
    @Field()
    @IsUUID()
    id: string
}