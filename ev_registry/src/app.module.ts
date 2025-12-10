import { Module } from '@nestjs/common';
import { CpModule } from './modules/cp/cp.module';
import { GraphQLModule } from '@nestjs/graphql';
import { ApolloDriver, ApolloDriverConfig } from '@nestjs/apollo';
import { TypeOrmModule } from '@nestjs/typeorm';
import { RegisterModule } from './modules/register/register.module';

@Module({
  imports: [
  GraphQLModule.forRoot<ApolloDriverConfig>({
    driver: ApolloDriver,
    graphiql: true,
    autoSchemaFile: true,
  }), 
  TypeOrmModule.forRoot({
    type: "postgres",
    host: process.env.DB_HOST || "localhost",
    port: Number(process.env.DB_PORT) || 5432,
    database:  process.env.DB_NAME || "evcharging",
    username:  process.env.DB_USER || "usuario",
    password:  process.env.DB_PASSWORD || "contraseña",

    entities: ["dist/**/*.entity{.ts,.js}"],
    synchronize: true
  }),
  CpModule,
  RegisterModule],
})
export class AppModule {}
