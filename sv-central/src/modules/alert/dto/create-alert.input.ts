import { InputType, Int, Field } from '@nestjs/graphql';

@InputType()
export class CreateAlertInput {
  @Field()
  ciudad: string;
}
