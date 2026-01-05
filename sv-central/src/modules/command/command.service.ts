import { Injectable } from '@nestjs/common';
import { CommandInput } from './dto/create-command.input';
import { CpService } from '../cp/cp.service';
import { ProducerService } from '../kafka/kafka.service';
import { CentralCpInput } from '../kafka/dto/central-cp-kafka.input';

@Injectable()
export class CommandService {
  constructor(
    private readonly cpService: CpService,
    private readonly producerService: ProducerService
  ){}

  async postCommand(commandInput: CommandInput): Promise<Boolean> {

    switch(commandInput.command){
      case "STOP":
        return this.stopPettiton(commandInput);
        break;
      case "BROKEN":
        return this.brokenPetition(commandInput);
        break;
      case "START":
        return this.startPetition(commandInput);
      break;
      case "UPDATE_PRICE":
        return this.updatePriceCp(commandInput);
      break;
      case "UPDATE_CITY":
        return this.updateCityCp(commandInput);
      break;
      case "UNLINK":
        return this.unlinkPetition(commandInput);
      break;
      default:
        return false
    }
  }
  
  //------------------------ CP FUNCIONALIDADES ------------------------
  unlinkPetition(commandInput: CommandInput): boolean { 
    //TODO enviar a cp la petición de desvinculación por kafka
    return true
  }
  
  
  stopPettiton(commandInput: CommandInput): boolean {
    console.log("Enviando STOP al CP "+commandInput.cpId);
    this.producerService.kafkaEmitToCP({
				cpId: commandInput.cpId,
				target: "ONE",
				action: "STOP",
    });
    return true
  }
  
  brokenPetition(commandInput: CommandInput): boolean {
    console.log("Enviando BROKEN al CP "+commandInput.cpId);
    this.producerService.kafkaEmitToCP({
      cpId: commandInput.cpId,
      target: "ONE",
      action: "BROKEN",
    });
    return true
  }
  startPetition(commandInput: CommandInput): boolean {
    console.log("Enviando START al CP "+commandInput.cpId);
    this.producerService.kafkaEmitToCP({
      cpId: commandInput.cpId,
      target: "ONE",
      action: "START",
    });
    return true
  }
  
  //------------------------ FRONT FUNCIONALIDADES ------------------------

  async updatePriceCp(commandInput: CommandInput): Promise<boolean> {
    
    const modCP = await this.cpService.findOne(commandInput.cpId)
    
    if (modCP){
      
      const kafkaInput: CentralCpInput = {
        action: "UPDATE_PRICE",
        target: "ONE",
        cpId: commandInput.cpId,
        newPrice: commandInput.newPrice,
      }

      await this.cpService.update({id: commandInput.cpId, precio_kwh: commandInput.newPrice})
      return await this.producerService.kafkaEmitToCP(kafkaInput)
    }
    return false
  }

  async updateCityCp(commandInput: CommandInput): Promise<boolean> {
    
    const modCP = await this.cpService.findOne(commandInput.cpId)
    
    if (modCP){
      
      const kafkaInput: CentralCpInput = {
        action: "UPDATE_PRICE",
        target: "ONE",
        cpId: commandInput.cpId,
        newCity: commandInput.newCity,
      }

      await this.cpService.update({id: commandInput.cpId, precio_kwh: commandInput.newPrice})
      return await this.producerService.kafkaEmitToCP(kafkaInput)
    }
    return false
  }
  
}
