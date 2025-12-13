import { Module } from '@nestjs/common';
import { AlertService } from './alert.service';
import { AlertResolver } from './alert.resolver';

@Module({
  providers: [AlertResolver, AlertService],
})
export class AlertModule {}
