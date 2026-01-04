import { Injectable, Inject } from '@nestjs/common';
import { ClientKafka } from '@nestjs/microservices';
import { KafkaTopics } from './kafka.topics';
import { lastValueFrom } from 'rxjs';
import { CentralCpInput } from './dto/central-cp-kafka.input';
import { CentralDriverInput } from './dto/central-driver-kafka.input';

@Injectable()
export class ProducerService {
    constructor(
        @Inject("KAFKA_SERVICE")
        private readonly kafkaClient: ClientKafka,
    ) {}

    async kafkaEmitToDriver(payload: CentralDriverInput) {
        try {
            await lastValueFrom(
                this.kafkaClient.emit(KafkaTopics.CENTRAL_DRIVER_COMMANDS, payload)
            )
            return true;
        } catch (error) {
            console.error("Kafka error", error)
            return false;
        }
    }

    async kafkaEmitToCP(payload: CentralCpInput): Promise<boolean> {
        try {
            await lastValueFrom(
                this.kafkaClient.emit(KafkaTopics.CENTRAL_CP_COMMANDS, payload)
            )
            return true;
        } catch (error) {
            console.error("Kafka error", error)
            return false;
        }
    }
}
