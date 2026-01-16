import { Injectable, Inject, Logger } from '@nestjs/common';
import { ClientKafka } from '@nestjs/microservices';
import { KafkaTopics } from './kafka.topics';
import { lastValueFrom } from 'rxjs';
import { CentralCpInput } from './dto/central-cp-kafka.input';
import { CentralDriverInput } from './dto/central-driver-kafka.input';
import { LogService } from '../logsmod/log.service';

@Injectable()
export class ProducerService {
    private readonly logger = new Logger(ProducerService.name);
    
    constructor(
        @Inject("KAFKA_SERVICE")
        private readonly kafkaClient: ClientKafka,
        private readonly logService: LogService
    ) {
        this.logger.log('ProducerService initialized');
    }

    async kafkaEmitToDriver(payload: CentralDriverInput) {
        this.logger.log(`Emitting message to Driver - Action: ${payload.action}, Driver ID: ${payload.driver_id || 'N/A'}`);
        this.logService.create(`Emitting message to Driver - Action: ${payload.action}, Driver ID: ${payload.driver_id || 'N/A'}`);
        try {
            await lastValueFrom(
                this.kafkaClient.emit(KafkaTopics.CENTRAL_DRIVER_COMMANDS, payload)
            );
            this.logger.log('Message sent to Driver successfully');
            this.logService.create('Message sent to Driver successfully');
            
            return true;
        } catch (error) {
            this.logger.error(`Failed to send message to Driver: ${error.message}`, error.stack);
            this.logService.create(`Failed to send message to Driver: ${error.message}`);
            return false;
        }
    }

    async kafkaEmitToCP(payload: CentralCpInput): Promise<boolean> {
        this.logger.log(`Emitting message to CP: ${payload.cpId} - Action: ${payload.action}`);
        this.logService.create(`Emitting message to CP: ${payload.cpId} - Action: ${payload.action}`);
        try {
            await lastValueFrom(
                this.kafkaClient.emit(KafkaTopics.CENTRAL_CP_COMMANDS, payload)
            );
            this.logger.log(`Message sent to CP ${payload.cpId} successfully`);
            this.logService.create(`Message sent to CP ${payload.cpId} successfully`);
            return true;
        } catch (error) {
            this.logger.error(`Failed to send message to CP ${payload.cpId}: ${error.message}`, error.stack);
            this.logService.create(`Failed to send message to CP ${payload.cpId}: ${error.message}`);
            return false;
        }
    }
}
