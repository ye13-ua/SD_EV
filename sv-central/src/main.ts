import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { readFileSync, existsSync } from "node:fs"
import { MicroserviceOptions, Transport } from '@nestjs/microservices';

async function bootstrap() {
  
  const certPath = existsSync("/certs/central.key") ? "/certs" : "../certs";
  const app = await NestFactory.create(AppModule, {
    httpsOptions:
      {
        key: readFileSync(`${certPath}/central.key`),
        cert: readFileSync(`${certPath}/central.crt`),
  },});
  
  // Habilitar CORS
  app.enableCors({
    origin: ['http://localhost:5173', 'http://localhost:3000', 'http://localhost:8862'], // Orígenes permitidos
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
  });
  
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
