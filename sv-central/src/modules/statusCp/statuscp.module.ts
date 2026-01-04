import { Module } from '@nestjs/common';
import { StatusCpService } from './statuscp.service';
import { StatusCpResolver } from './statuscp.resolver';
import { CpModule } from '../cp/cp.module';


@Module({
  imports: [CpModule],
  providers: [StatusCpService, StatusCpResolver],
  exports: [StatusCpService],

})
export class StatusCpModule {}
