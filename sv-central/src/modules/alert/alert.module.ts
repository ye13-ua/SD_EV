import { Module } from '@nestjs/common';
import { AlertService } from './alert.service';
import { AlertResolver } from './alert.resolver';
import { LogModule } from '../logsmod/log.module';

@Module({
  imports: [LogModule],
  providers: [AlertResolver, AlertService],
  exports: [AlertService],
})
export class AlertModule {}
