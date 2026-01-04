import { Module } from '@nestjs/common';
import { StatusCpService } from './statuscp.service';
import { StatusCpResolver } from './statuscp.resolver';
import { CpModule } from '../cp/cp.module';
import { AlertModule } from '../alert/alert.module';
import { CommandModule } from '../command/command.module';


@Module({
  imports: [CpModule, AlertModule, CommandModule],
  providers: [StatusCpService, StatusCpResolver],
  exports: [StatusCpService],

})
export class StatusCpModule {}
