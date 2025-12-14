import { Controller } from '@nestjs/common';
import { ProducerService } from './kafka.service';
import { MessagePattern, Payload } from '@nestjs/microservices';
import { KafkaTopics } from './kafka.topìcs';

@Controller()
export class KafkaController {
  constructor(private readonly producerService: ProducerService) {}

  @MessagePattern(KafkaTopics.DRIVER_COMMANDS)
  handle(@Payload() payload: any) {
    if(payload.action === "READALL"){
      
    }
    if(payload.action === "CONNECTCP"){
      
    }
    if(payload.action === "DISCONNECT"){
      
    }
    if(payload.action === "REGISTER"){
      
    }
  }

}

