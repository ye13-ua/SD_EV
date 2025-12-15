import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import * as fs from "node:fs"
import { MicroserviceOptions, Transport } from '@nestjs/microservices';

async function bootstrap() {
  
  
  //TODO cambiar el archivo de certs al que esta en docker
  const app = await NestFactory.create(AppModule, {httpsOptions:
      {
        key: fs.readFileSync("../certs/registry.key"),
        cert: fs.readFileSync("../certs/registry.crt"),
  },});
  
  app.connectMicroservice<MicroserviceOptions>({
    transport: Transport.KAFKA,
    options: {
      client: {
        brokers: [process.env.KAFKA_BROKER ?? "localhost:9092"]
      },
      consumer: {
        groupId: process.env.KAFKA_GROUPID ?? "commands-service"
      }
    }
  })
  
  await app.startAllMicroservices();
  await app.listen(process.env.PORT ?? 4000);
}

bootstrap();
