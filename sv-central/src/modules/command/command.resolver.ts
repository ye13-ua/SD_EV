import { Resolver, Mutation, Args } from '@nestjs/graphql';
import { CommandService } from './command.service';
import { Command } from './entities/command.entity';
import { CommandInput } from './dto/create-command.input';

@Resolver(() => Command)
export class CommandResolver {
  constructor(private readonly commandService: CommandService) {}

  @Mutation(() => Boolean, {name: "postCommand", description: "Aqui se envian los comandos y se procesan"})
  postCommand(@Args('commandInput') commandInput: CommandInput): Promise<Boolean> {
    return this.commandService.postCommand(commandInput);
  }

}
