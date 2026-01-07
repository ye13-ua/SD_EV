import { Injectable, Logger } from '@nestjs/common';
import { CommandInput } from './dto/create-command.input';
import { CpService } from '../cp/cp.service';
import { ProducerService } from '../kafka/kafka.service';
import { CentralCpInput } from '../kafka/dto/central-cp-kafka.input';

@Injectable()
export class CommandService {
  private readonly logger = new Logger(CommandService.name);
  
  constructor(
    private readonly cpService: CpService,
    private readonly producerService: ProducerService
  ){
    this.logger.log('CommandService initialized');
  }

  async postCommand(commandInput: CommandInput): Promise<Boolean> {
    this.logger.log(`Received command: ${commandInput.command} for CP: ${commandInput.cpId}`);

    switch(commandInput.command){
      case "STOP":
        return this.stopPettiton(commandInput);
      case "STOP_COLD":
        return this.stopColdPetition(commandInput);
      case "BROKEN":
        return this.brokenPetition(commandInput);
      case "START":
        return this.startPetition(commandInput);
      case "UPDATE_PRICE":
        return this.updatePriceCp(commandInput);
      case "UPDATE_CITY":
        return this.updateCityCp(commandInput);
      case "UNLINK":
        return this.unlinkPetition(commandInput);
      case "TICKET":
        return this.finishedChargingPetition(commandInput);
      default:
        this.logger.warn(`Unknown command: ${commandInput.command}`);
        return false;
    }
  }
  
  //------------------------ CP FUNCIONALIDADES ------------------------
  finishedChargingPetition(commandInput: CommandInput): boolean {
    this.logger.debug(`Preparing to send TICKET command: CP: ${commandInput.cpId}, Driver: ${commandInput.driverId}, Price: ${commandInput.price}`);
    if (!commandInput.driverId || !commandInput.price) {
      this.logger.error(`Missing driverId or price for TICKET command for CP: ${commandInput.cpId}`);
      return false;
    }
    
    this.logger.log(`Sending TICKET command to Driver: ${commandInput.driverId}`);
    
    const ticketPayload = {
      driver_id: commandInput.driverId,
      action: "TICKET" as const,
      cp_id: commandInput.cpId,
      price: commandInput.price,
    };
    
    this.logger.debug(`[TICKET ENVIADO] Payload completo: ${JSON.stringify(ticketPayload)}`);
    
    this.producerService.kafkaEmitToDriver(ticketPayload);
    
    this.logger.log(`FINISHED_CHARGING command sent to Driver: ${commandInput.driverId} with data CP: ${commandInput.cpId} and Price: ${commandInput.price}`);
    
    return true;
  }

  stopColdPetition(commandInput: CommandInput): boolean {
    this.logger.log(`Sending STOP_COLD command to CP: ${commandInput.cpId}`);
    this.producerService.kafkaEmitToCP({ 
      cpId: commandInput.cpId,
      target: "ONE",
      action: "STOP_COLD",
    });
    this.logger.log(`STOP_COLD command sent to CP: ${commandInput.cpId}`);
    return true;
  }

  unlinkPetition(commandInput: CommandInput): boolean { 
    this.logger.log(`Unlinking CP: ${commandInput.cpId}`);
    this.cpService.unlink(commandInput.cpId);
    this.logger.log(`CP ${commandInput.cpId} unlinked successfully`);
    return true;
  }
  
  
  stopPettiton(commandInput: CommandInput): boolean {
    this.logger.log(`Sending STOP command to CP: ${commandInput.cpId}`);
    this.producerService.kafkaEmitToCP({
			cpId: commandInput.cpId,
			target: "ONE",
			action: "STOP",
    });
    this.logger.log(`STOP command sent to CP: ${commandInput.cpId}`);
    return true;
  }
  
  brokenPetition(commandInput: CommandInput): boolean {
    this.logger.log(`Sending BROKEN command to CP: ${commandInput.cpId}`);
    this.producerService.kafkaEmitToCP({
      cpId: commandInput.cpId,
      target: "ONE",
      action: "BROKEN",
    });
    this.logger.log(`BROKEN command sent to CP: ${commandInput.cpId}`);
    return true;
  }
  
  startPetition(commandInput: CommandInput): boolean {
    this.logger.log(`Sending START command to CP: ${commandInput.cpId}`);
    this.producerService.kafkaEmitToCP({
      cpId: commandInput.cpId,
      target: "ONE",
      action: "START",
    });
    this.logger.log(`START command sent to CP: ${commandInput.cpId}`);
    return true;
  }
  
  //------------------------ FRONT FUNCIONALIDADES ------------------------

  async updatePriceCp(commandInput: CommandInput): Promise<boolean> {
    this.logger.log(`Updating price for CP: ${commandInput.cpId} to ${commandInput.newPrice}`);
    
    const modCP = await this.cpService.findOne(commandInput.cpId);
    
    if (modCP){
      
      const kafkaInput: CentralCpInput = {
        action: "UPDATE_PRICE",
        target: "ONE",
        cpId: commandInput.cpId,
        newPrice: commandInput.newPrice,
      }

      await this.cpService.update({id: commandInput.cpId, precio_kwh: commandInput.newPrice});
      this.logger.log(`Price updated for CP: ${commandInput.cpId}`);
      return await this.producerService.kafkaEmitToCP(kafkaInput);
    }
    this.logger.error(`Failed to update price - CP not found: ${commandInput.cpId}`);
    return false;
  }

  async updateCityCp(commandInput: CommandInput): Promise<boolean> {
    this.logger.log(`Updating city for CP: ${commandInput.cpId} to ${commandInput.newCity}`);
    
    const modCP = await this.cpService.findOne(commandInput.cpId);
    
    if (modCP){
      
      const kafkaInput: CentralCpInput = {
        action: "UPDATE_CITY",
        target: "ONE",
        cpId: commandInput.cpId,
        newCity: commandInput.newCity,
      }

      await this.cpService.update({id: commandInput.cpId, ciudad: commandInput.newCity});
      this.logger.log(`City updated for CP: ${commandInput.cpId}`);
      return await this.producerService.kafkaEmitToCP(kafkaInput);
    }
    this.logger.error(`Failed to update city - CP not found: ${commandInput.cpId}`);
    return false;
  }
  
}
