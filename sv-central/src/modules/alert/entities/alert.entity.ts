import { ObjectType, Field, Int } from '@nestjs/graphql';

@ObjectType()
export class Alert {
  @Field(() => String)
  ciudad: string;
}
