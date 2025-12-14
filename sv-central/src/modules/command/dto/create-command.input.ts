import { InputType, Float, Field } from '@nestjs/graphql';

@InputType()
export class CommandInput {
  // CHARGING_PETTITION - 
  @Field(() => String)
  command: string;

  @Field(() => String, {nullable: true})
  cpId: string

  @Field(() => String, {nullable: true})
  targetId: string

  @Field(() => String, {nullable: true})
  driverId: string

  @Field(() => Float, {nullable: true})
  targetCharge: number

  @Field(() => Float, {nullable: true})
  newPrice: number

  @Field(() => String, {nullable: true})
  newCity: string

}
