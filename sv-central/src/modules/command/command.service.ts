import { Injectable } from '@nestjs/common';
import { CommandInput } from './dto/create-command.input';
import { CpService } from '../cp/cp.service';

@Injectable()
export class CommandService {
  constructor(private readonly cpService: CpService){}
  async postCommand(commandInput: CommandInput): Promise<Boolean> {

    switch(commandInput.command){
      case "CHARGING_PETITION":
        return this.chargingPetition(commandInput);
      break;
      case "UPDATE":
        return this.updateCp(commandInput);
      break;
      default:
        return false
    }
  }
  
  //------------------------ CP FUNCIONALIDADES ------------------------
  chargingPetition(commandInput: CommandInput): boolean {
    //TODO
    return true
  }

  //------------------------ FRONT FUNCIONALIDADES ------------------------

  updateCp(commandInput: CommandInput): boolean {
    if (commandInput.newCity)
      this.cpService.update({id: commandInput.cpId, ciudad: commandInput.newCity})
    
    if (commandInput.newPrice)
      this.cpService.update({id: commandInput.cpId, precio_kwh: commandInput.newPrice})
    //TODO POST TO KAFKA
    
    return true
  }
  
}
