import { CommandInput } from './create-command.input';
import { InputType, Field, Int, PartialType } from '@nestjs/graphql';

@InputType()
export class UpdateCommandInput extends PartialType(CommandInput) {
  @Field(() => Int)
  id: number;
}
