import { InputType, Int, Field } from '@nestjs/graphql';

@InputType()
export class CreateLogInput {
  @Field(() => Number, { description: 'TimeStamp of the action' })
  timestamp: number;

  @Field(() => String)
  description: string
}
