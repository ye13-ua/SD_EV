import { Module } from '@nestjs/common';
import { CpService } from './cp.service';
import { CpResolver } from './cp.resolver';
import { TypeOrmModule } from '@nestjs/typeorm';
import { CP } from './entities/cp.entity';

@Module({
  imports: [TypeOrmModule.forFeature([CP])],
  providers: [CpService, CpResolver]
})
export class CpModule {}
