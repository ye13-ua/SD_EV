import { ObjectType, Field, Int } from '@nestjs/graphql';

@ObjectType()
export class Command {
  @Field(() => Int, { description: 'Example field (placeholder)' })
  exampleField: number;
}
