import { Module, forwardRef } from '@nestjs/common';
import { CommandService } from './command.service';
import { CommandResolver } from './command.resolver';
import { CpModule } from '../cp/cp.module';
import { KafkaModule } from '../kafka/kafka.module';
import { StatusCpModule } from '../statusCp/statuscp.module';
import { LogModule } from '../logsmod/log.module';

@Module({
  providers: [CommandResolver, CommandService],
  imports: [CpModule, forwardRef(() => KafkaModule), forwardRef(() => StatusCpModule), forwardRef(() => LogModule)],
  exports: [CommandService]
})
export class CommandModule {}
