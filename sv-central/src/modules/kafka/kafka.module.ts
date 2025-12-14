import { Module } from '@nestjs/common';
import { ProducerService } from './kafka.service';
import { KafkaController } from './kafka.controller';
import { ClientsModule, Transport } from '@nestjs/microservices';



@Module({
  imports:[
    ClientsModule.register([
    {
      name: "KAFKA_SERVICE",
      transport: Transport.KAFKA,
      options: {
        client: {
          brokers: [process.env.KAFKA_BROKER ?? "kafka:9092"]
        },
        consumer: {
          groupId: process.env.KAFKA_GROUPID ?? "commands-service"
        }
      },
    }
  ])],
  controllers: [KafkaController],
  providers: [ProducerService],
  exports: [ProducerService, KafkaController]
})
export class KafkaModule {}
