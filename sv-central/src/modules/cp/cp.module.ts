import { Module } from '@nestjs/common';
import { CpService } from './cp.service';
import { CpResolver } from './cp.resolver';
import { TypeOrmModule } from '@nestjs/typeorm';
import { CP } from './entities/cp.entity';
import { LogModule } from '../logsmod/log.module';

@Module({
  imports: [TypeOrmModule.forFeature([CP]), LogModule],
  providers: [CpService, CpResolver],
  exports: [CpService]
})
export class CpModule {}
