import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';
import * as fs from "node:fs"

async function bootstrap() {
  const app = await NestFactory.create(AppModule, 
    {httpsOptions:
    {
      key: fs.readFileSync("../certs/registry.key"),
      cert: fs.readFileSync("../certs/registry.crt"),
    },}
  );
  app.useGlobalPipes(new ValidationPipe())
  await app.listen(process.env.PORT ?? 4001);
}
bootstrap();
