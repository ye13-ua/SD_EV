import { Module, forwardRef } from '@nestjs/common';
import { ProducerService } from './kafka.service';
import { KafkaController } from './kafka.controller';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { StatusCpModule } from '../statusCp/statuscp.module';
import { CpModule } from '../cp/cp.module';



@Module({
  imports:[
    ClientsModule.register([
    {
      name: "KAFKA_SERVICE",
      transport: Transport.KAFKA,
      options: {
        client: {
          brokers: [process.env.KAFKA_BROKER ?? "localhost:9092"]
        },
        consumer: {
          groupId: process.env.KAFKA_GROUPID ?? "commands-service"
        }
      },
    }
  ]), forwardRef(() => StatusCpModule), CpModule],
  controllers: [KafkaController],
  providers: [ProducerService],
  exports: [ProducerService]
})
export class KafkaModule {}
