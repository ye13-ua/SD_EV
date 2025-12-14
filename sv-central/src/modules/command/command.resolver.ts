import { Resolver, Query, Mutation, Args, Int } from '@nestjs/graphql';
import { CommandService } from './command.service';
import { Command } from './entities/command.entity';
import { CreateCommandInput } from './dto/create-command.input';
import { UpdateCommandInput } from './dto/update-command.input';

@Resolver(() => Command)
export class CommandResolver {
  constructor(private readonly commandService: CommandService) {}

  @Mutation(() => Command)
  createCommand(@Args('createCommandInput') createCommandInput: CreateCommandInput) {
    return this.commandService.create(createCommandInput);
  }

  @Query(() => [Command], { name: 'command' })
  findAll() {
    return this.commandService.findAll();
  }

  @Query(() => Command, { name: 'command' })
  findOne(@Args('id', { type: () => Int }) id: number) {
    return this.commandService.findOne(id);
  }

  @Mutation(() => Command)
  updateCommand(@Args('updateCommandInput') updateCommandInput: UpdateCommandInput) {
    return this.commandService.update(updateCommandInput.id, updateCommandInput);
  }

  @Mutation(() => Command)
  removeCommand(@Args('id', { type: () => Int }) id: number) {
    return this.commandService.remove(id);
  }
}
