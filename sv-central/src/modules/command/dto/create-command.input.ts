import { InputType, Float, Field } from '@nestjs/graphql';

@InputType()
export class CommandInput {
  // CHARGING_PETTITION - 
  @Field(() => String)
  command: "STOP" | "START" | "BROKEN" | "UPDATE_PRICE" | "UPDATE_CITY" | "UNLINK";

  @Field(() => String, {nullable: true})
  cpId: string

  @Field(() => String, {nullable: true})
  target: "ONE" | "ALL"

  @Field(() => String, {nullable: true})
  driverId?: string

  @Field(() => Float, {nullable: true})
  targetCharge?: number

  @Field(() => Float, {nullable: true})
  newPrice?: number

  @Field(() => String, {nullable: true})
  newCity?: string

}
