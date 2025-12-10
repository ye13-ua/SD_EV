import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';
import { readFileSync } from "node:fs"

async function bootstrap() {
  const app = await NestFactory.create(AppModule, 
    //TODO https para docker
    {httpsOptions:
    {
      key: readFileSync("../certs/registry.key"),
      cert: readFileSync("../certs/registry.crt"),
    },}
  );
  app.useGlobalPipes(new ValidationPipe())
  await app.listen(process.env.PORT ?? 4001);
}
bootstrap();
