import { Module } from '@nestjs/common';
import { RegisterService } from './register.service';
import { RegisterResolver } from './register.resolver';

@Module({
  providers: [RegisterResolver, RegisterService],
})
export class RegisterModule {}
