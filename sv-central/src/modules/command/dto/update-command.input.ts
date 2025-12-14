import { CreateCommandInput } from './create-command.input';
import { InputType, Field, Int, PartialType } from '@nestjs/graphql';

@InputType()
export class UpdateCommandInput extends PartialType(CreateCommandInput) {
  @Field(() => Int)
  id: number;
}
