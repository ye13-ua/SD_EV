import { Module, forwardRef } from '@nestjs/common';
import { StatusCpService } from './statuscp.service';
import { StatusCpResolver } from './statuscp.resolver';
import { CpModule } from '../cp/cp.module';
import { AlertModule } from '../alert/alert.module';
import { CommandModule } from '../command/command.module';
import { LogModule } from '../logsmod/log.module';


@Module({
  imports: [CpModule, AlertModule, forwardRef(() => CommandModule), LogModule],
  providers: [StatusCpService, StatusCpResolver],
  exports: [StatusCpService],

})
export class StatusCpModule {}
