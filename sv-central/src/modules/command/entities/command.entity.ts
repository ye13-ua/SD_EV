import { ObjectType, Field, Float } from '@nestjs/graphql';

@ObjectType()
export class Command {
  @Field(() => String)
  command: string;

  @Field(() => String, {nullable: true})
  cpId: string

  //UUID / ALL
  @Field(() => String, {nullable: true})
  target: string

  @Field(() => String, {nullable: true})
  driverId: string

  @Field(() => Float, {nullable: true})
  targetCharge: number

  @Field(() => Float, {nullable: true})
  newPrice: number

  @Field(() => String, {nullable: true})
  newCity: string
}
