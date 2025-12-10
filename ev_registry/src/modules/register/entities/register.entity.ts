import { ObjectType, Field, Int } from '@nestjs/graphql';

@ObjectType()
export class Register {
  @Field(() => Int, { description: 'Example field (placeholder)' })
  exampleField: number;
}
