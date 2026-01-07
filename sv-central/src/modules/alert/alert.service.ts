import { Injectable, Logger } from '@nestjs/common';
import { CreateAlertInput } from './dto/create-alert.input';
import { Alert } from './entities/alert.entity';

@Injectable()
export class AlertService {
  private readonly logger = new Logger(AlertService.name);
  private alerts = new Map<string, Alert>();

  create(createAlertInput: CreateAlertInput): Alert {
    this.logger.log(`Creating alert for city: ${createAlertInput.ciudad}`);
    const alerta = new Alert();
    alerta.ciudad = createAlertInput.ciudad;
    this.alerts.set(alerta.ciudad, alerta);
    this.logger.log(`Alert created for city: ${alerta.ciudad}`);
    return alerta;
  }

  findAll(): Alert[] {
    this.logger.debug(`Finding all alerts (${this.alerts.size} total)`);
    return [...this.alerts.values()];
  }

  remove(ciudad: string): boolean {
    this.logger.log(`Removing alert for city: ${ciudad}`);
    const removed = this.alerts.delete(ciudad);
    if (removed) {
      this.logger.log(`Alert removed for city: ${ciudad}`);
    } else {
      this.logger.warn(`Alert not found for city: ${ciudad}`);
    }
    return removed;
  }
}
