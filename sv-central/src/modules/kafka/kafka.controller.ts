import { Controller } from '@nestjs/common';
import { ProducerService } from './kafka.service';
import { MessagePattern, Payload } from '@nestjs/microservices';
import { KafkaTopics } from './kafka.topìcs';
import { DriverCentralInput } from './dto/driver-central-kafka.input';
import { StatusCpService } from '../statusCp/statuscp.service';
import { CentralDriverInput } from './dto/central-driver-kafka.input';
import { CpService } from '../cp/cp.service';
import { CentralCpInput } from './dto/central-cp-kafka.input';

@Controller()
export class KafkaController {
  constructor(
    private readonly producerService: ProducerService,
    private readonly statusCpService :StatusCpService,
    private readonly CpService :CpService
  ) {}

  @MessagePattern(KafkaTopics.DRIVER_COMMANDS)
  handle(@Payload() payload: DriverCentralInput) {
    switch(payload.action){
      case "READALL":
        return this.readAllAction(payload)
      break;
      case "CONNECTCP":
        return this.connectCpAction(payload)
      break;
      case "DISCONNECT":
        return this.disconnectAction(payload)
      break;
      case "REGISTER":
        return this.registerAction(payload)
      break;
      default:
        console.error("Wrong action");
    }
  }

  async readAllAction(payload: DriverCentralInput): Promise<boolean>{
    const activeCP = this.statusCpService.readAllActiveStatusCP()
    const allCps = await this.CpService.findAll()

    const cpsPayload: Array<{
      id: string
      ciudad: string
      calle: string
      precio: number
      estado: string
    }> = []
    
    activeCP.forEach((acp, i) => {
      const cp = allCps.find((cp) => {cp.id === acp.id})
      
      cpsPayload[i].id = acp.id;
      cpsPayload[i].ciudad = cp?.ciudad ?? "N/A";
      cpsPayload[i].calle = cp?.calle ?? "N/A";
      cpsPayload[i].precio = acp.price ?? cp?.precio_kwh ?? -1;
      cpsPayload[i].estado = acp.estado ?? "DESCONOCIDO";

    })

    const centralDriverInput: CentralDriverInput = {
      action: "READALL_RESPONSE",
      driver_id: payload.driver_id,
      cps: cpsPayload,
    }

    return this.producerService.kafkaEmitToDriver(centralDriverInput) 
  }

  async connectCpAction(payload: DriverCentralInput): Promise<boolean>{
    
    const connectCP = this.statusCpService.readAllActiveStatusCP().find((cp) => {cp.id === payload.cp_id})

     const centralDriverInput: CentralDriverInput = {
        action: "CONNECT_CP_RESPONSE",
        driver_id: payload.driver_id,
      }

    if(connectCP !== undefined){
      
      const centraCpInput: CentralCpInput = {
        target: "ONE",
        action: "CHARGE",
        cpId: connectCP.id,
        driverId: payload.driver_id,
        target_charge: payload.charge
      }

      centralDriverInput.isValidated = await this.producerService.kafkaEmitToCP(centraCpInput)
      centralDriverInput.cp_id = connectCP.id

    } 

    return await this.producerService.kafkaEmitToDriver(centralDriverInput)

  }

  async disconnectAction(payload: DriverCentralInput): Promise<boolean>{
      
    const centralDriverInput: CentralDriverInput = {
      action: "DISCONNECT",
      driver_id: payload.driver_id,
      cp_id: payload.cp_id
    }

    const centraCpInput: CentralCpInput = {
      target: "ONE",
      action: "DRIVER_DISCONNECT",
      cpId: payload.cp_id,
      driverId: payload.driver_id,
    }
    
    return (
      await this.producerService.kafkaEmitToDriver(centralDriverInput) && 
      await this.producerService.kafkaEmitToCP(centraCpInput)
    )
  }

  async registerAction(payload: DriverCentralInput): Promise<boolean>{
    
    return true; 
  }

}

