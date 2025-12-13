import { Injectable } from '@nestjs/common';
import { CreateAlertInput } from './dto/create-alert.input';
import { Alert } from './entities/alert.entity';

@Injectable()
export class AlertService {
  private alerts = new Map<string, Alert>

  create(createAlertInput: CreateAlertInput): Alert {
    const alerta = new Alert();
    alerta.ciudad = createAlertInput.ciudad
    this.alerts.set(alerta.ciudad, alerta)
    return alerta
  }

  findAll(): Alert[] {
    return [...this.alerts.values()];
  }

  remove(ciudad: string): boolean {
    return this.alerts.delete(ciudad)
  }
}
