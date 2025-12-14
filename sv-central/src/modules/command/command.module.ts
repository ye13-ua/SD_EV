import { Module } from '@nestjs/common';
import { CommandService } from './command.service';
import { CommandResolver } from './command.resolver';

@Module({
  providers: [CommandResolver, CommandService],
})
export class CommandModule {}
