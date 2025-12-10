import { CreateRegisterInput } from './create-register.input';
import { InputType, Field, Int, PartialType } from '@nestjs/graphql';

@InputType()
export class UpdateRegisterInput extends PartialType(CreateRegisterInput) {
  @Field(() => Int)
  id: number;
}
