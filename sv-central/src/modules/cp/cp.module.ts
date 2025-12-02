import { Module } from '@nestjs/common';
import { CpService } from './cp.service';
import { CpResolver } from './cp.resolver';

@Module({
  providers: [CpService, CpResolver]
})
export class CpModule {}
