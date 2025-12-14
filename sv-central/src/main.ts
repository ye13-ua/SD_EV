import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import * as fs from "node:fs"
import { MicroserviceOptions, Transport } from '@nestjs/microservices';
import { ConfigService } from '@nestjs/config';



async function bootstrap() {
  
  
  //TODO cambiar el archivo de certs al que esta en docker
  const app = await NestFactory.create(AppModule, {httpsOptions:
      {
        key: fs.readFileSync("../certs/registry.key"),
        cert: fs.readFileSync("../certs/registry.crt"),
  },});
  
  const configService = app.get(ConfigService);

  app.connectMicroservice<MicroserviceOptions>({
    transport: Transport.KAFKA,
    options: {
      client: {
        brokers: [configService.get<string>("KAFKA_BROKER", "kafka:9092")]
      },
      consumer: {
        groupId: configService.get<string>("KAFKA_GROUPID", "commands-service")
      }
    }
  })
  
  await app.startAllMicroservices();
  await app.listen(process.env.PORT ?? 4000);
}

bootstrap();
