import { Module } from '@nestjs/common';
import { GraphQLModule } from '@nestjs/graphql';
import { ApolloDriver, ApolloDriverConfig } from '@nestjs/apollo';
import { CpModule } from './modules/cp/cp.module';
import { AlertModule } from './modules/alert/alert.module';
import { TypeOrmModule } from '@nestjs/typeorm';

@Module({
  imports: [
  GraphQLModule.forRoot<ApolloDriverConfig>({
    driver: ApolloDriver,
    graphiql: true,
    autoSchemaFile: true,
  }), 
  TypeOrmModule.forRoot({
    type: "postgres",
    database: ":memory:",
    entities: ["dist/**/*.entity{.ts,.js}"],
    synchronize: true
  }),
  CpModule, 
  AlertModule,
  

  ],
})
export class AppModule {}
