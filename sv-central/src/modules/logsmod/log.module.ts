import { Module } from '@nestjs/common';
import { LogService } from './log.service';
import { LogResolver } from './log.resolver';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Log } from './entities/log.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Log])],
  providers: [LogResolver, LogService],
  exports: [LogService],
})
export class LogModule {}
