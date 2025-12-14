import { Module } from '@nestjs/common';
import { CommandService } from './command.service';
import { CommandResolver } from './command.resolver';
import { CpModule } from '../cp/cp.module';

@Module({
  providers: [CommandResolver, CommandService],
  imports: [CpModule]
})
export class CommandModule {}
