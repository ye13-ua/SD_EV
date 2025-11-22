import { Module } from '@nestjs/common';
import { CpsController } from './cps.controller';
import { CpsService } from './cps.service';

@Module({
  controllers: [CpsController],
  providers: [CpsService]
})
export class CpsModule {}
