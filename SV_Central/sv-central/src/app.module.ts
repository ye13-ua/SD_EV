import { Module } from '@nestjs/common';
import { CpsModule } from './modules/cps/cps.module';
import { CpsController } from './modules/cps/cps.controller';
import { GraphQLModule } from "@nestjs/graphql"
import { graphqlConfig } from './config/graphql.config';
@Module({
  imports: [
    GraphQLModule.forRoot(graphqlConfig),
    CpsModule],
  controllers: [CpsController],
})
export class AppModule {}
