import { Module } from '@nestjs/common';
import { StatusCpService } from './statuscp.service';
import { StatusCpResolver } from './statuscp.resolver';


@Module({
  providers: [StatusCpService, StatusCpResolver],
  exports: [StatusCpResolver],

})
export class StatusCpModule {}
