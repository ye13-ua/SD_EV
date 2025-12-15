import { Module } from '@nestjs/common';
import { StatusCpService } from './statuscp.service';
import { StatusCpResolver } from './statuscp.resolver';


@Module({
  providers: [StatusCpService, StatusCpResolver],
  exports: [StatusCpService],

})
export class StatusCpModule {}
