import { Module } from '@nestjs/common';
import { CommandService } from './command.service';
import { CommandResolver } from './command.resolver';
import { CpModule } from '../cp/cp.module';
import { KafkaModule } from '../kafka/kafka.module';
import { StatusCpModule } from '../statusCp/statuscp.module';

@Module({
  providers: [CommandResolver, CommandService],
  imports: [CpModule, KafkaModule, StatusCpModule]
})
export class CommandModule {}
