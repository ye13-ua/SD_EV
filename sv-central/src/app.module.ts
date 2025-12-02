import { Module } from '@nestjs/common';
import { GraphQLModule } from '@nestjs/graphql';
import { ApolloDriver, ApolloDriverConfig } from '@nestjs/apollo';
import { CpModule } from './cp/cp.module';
import { LogsModule } from './logs/logs.module';
import { TicketModule } from './ticket/ticket.module';
import { AlertModule } from './modules/alert/alert.module';

@Module({
  imports: [GraphQLModule.forRoot<ApolloDriverConfig>({
    driver: ApolloDriver,
    graphiql: true,
    autoSchemaFile: true,
  }), CpModule, LogsModule, TicketModule, AlertModule],
})
export class AppModule {}
