import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';
import { readFileSync, existsSync } from "node:fs"

async function bootstrap() {
  // Ruta para Docker o local
  const certPath = existsSync("/certs/registry.key") ? "/certs" : "../certs";
  
  const app = await NestFactory.create(AppModule, 
    {httpsOptions:
    {
      key: readFileSync(`${certPath}/registry.key`),
      cert: readFileSync(`${certPath}/registry.crt`),
    },}
  );
  app.useGlobalPipes(new ValidationPipe())
  await app.listen(process.env.PORT ?? 4001);
}
bootstrap();
