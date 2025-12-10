import { Resolver, Query, Mutation, Args, Int } from '@nestjs/graphql';
import { RegisterService } from './register.service';
import { Register } from './entities/register.entity';
import { CreateRegisterInput } from './dto/create-register.input';
import { UpdateRegisterInput } from './dto/update-register.input';

@Resolver(() => Register)
export class RegisterResolver {
  constructor(private readonly registerService: RegisterService) {}

  @Mutation(() => Register)
  createRegister(@Args('createRegisterInput') createRegisterInput: CreateRegisterInput) {
    return this.registerService.create(createRegisterInput);
  }

  @Query(() => [Register], { name: 'register' })
  findAll() {
    return this.registerService.findAll();
  }

  @Query(() => Register, { name: 'register' })
  findOne(@Args('id', { type: () => Int }) id: number) {
    return this.registerService.findOne(id);
  }

  @Mutation(() => Register)
  updateRegister(@Args('updateRegisterInput') updateRegisterInput: UpdateRegisterInput) {
    return this.registerService.update(updateRegisterInput.id, updateRegisterInput);
  }

  @Mutation(() => Register)
  removeRegister(@Args('id', { type: () => Int }) id: number) {
    return this.registerService.remove(id);
  }
}
