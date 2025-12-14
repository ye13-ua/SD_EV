import { Injectable, Inject } from '@nestjs/common';
import { ClientKafka } from '@nestjs/microservices';
import { KafkaTopics } from './kafka.topìcs';

@Injectable()
export class ProducerService {
    constructor(
        @Inject("KAFKA_SERVICE")
        private readonly kafkaClient: ClientKafka,
    ) {}

    kafkaEmitToDriver(payload: any) {
        this.kafkaClient.emit(KafkaTopics.CENTRAL_DRIVER_COMMANDS, payload);
    }

    kafkaEmitToCP(payload: any) {
        this.kafkaClient.emit(KafkaTopics.CENTRAL_CP_COMMANDS, payload);
    }
}
