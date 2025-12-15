import { Module } from '@nestjs/common';
import { GraphQLModule } from '@nestjs/graphql';
import { ApolloDriver, ApolloDriverConfig } from '@nestjs/apollo';
import { CpModule } from './modules/cp/cp.module';
import { TypeOrmModule } from '@nestjs/typeorm';
import { StatusCpModule } from './modules/statusCp/statuscp.module';
import { AlertModule } from './modules/alert/alert.module';
import { ScheduleModule } from '@nestjs/schedule';
import { LogModule } from './modules/logsmod/log.module';
import { CommandModule } from './modules/command/command.module';
import { ConfigModule } from '@nestjs/config';
import { KafkaModule } from './modules/kafka/kafka.module';

@Module({
  imports: [
  ConfigModule.forRoot({
    isGlobal: true,
  }),
  GraphQLModule.forRoot<ApolloDriverConfig>({
    driver: ApolloDriver,
    graphiql: true,
    autoSchemaFile: true,
  }), 
  TypeOrmModule.forRoot({
    type: "postgres",
    host: process.env.DB_HOST ?? "localhost",
    port: Number(process.env.DB_PORT) ?? 5432,
    database:  process.env.DB_NAME ?? "evcharging",
    username:  process.env.DB_USER ?? "usuario",
    password:  process.env.DB_PASSWORD ?? "contraseña",

    entities: ["dist/**/*.entity{.ts,.js}"],
    synchronize: true
  }),
  CpModule, 
  AlertModule,
  StatusCpModule,
  ScheduleModule.forRoot(),
  LogModule,
  CommandModule,
  KafkaModule
  ],
})
export class AppModule {}
