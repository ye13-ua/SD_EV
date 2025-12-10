import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import * as fs from "node:fs"

async function bootstrap() {
  //TODO cambiar el archivo de certs al que esta en docker
  const app = await NestFactory.create(AppModule, {httpsOptions:
      {
        key: fs.readFileSync("../certs/registry.key"),
        cert: fs.readFileSync("../certs/registry.crt"),
      },});
  await app.listen(process.env.PORT ?? 4000);
}
bootstrap();
