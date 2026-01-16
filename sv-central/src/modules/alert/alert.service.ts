import { Injectable, Logger } from '@nestjs/common';
import { CreateAlertInput } from './dto/create-alert.input';
import { Alert } from './entities/alert.entity';
import { LogService } from '../logsmod/log.service';

@Injectable()
export class AlertService {
  constructor(
    private readonly logService: LogService,
  ) {}
  private readonly logger = new Logger(AlertService.name);
  private alerts = new Map<string, Alert>();

  create(createAlertInput: CreateAlertInput): Alert {
    this.logger.log(`Creating alert for city: ${createAlertInput.ciudad}`);
    this.logService.create(`Creating alert for city: ${createAlertInput.ciudad}`);
    const alerta = new Alert();
    alerta.ciudad = createAlertInput.ciudad;
    this.alerts.set(alerta.ciudad, alerta);
    this.logger.log(`Alert created for city: ${alerta.ciudad}`);
    this.logService.create(`Alert created for city: ${alerta.ciudad}`);
    return alerta;
  }

  findAll(): Alert[] {
    this.logger.debug(`Finding all alerts (${this.alerts.size} total)`);
    this.logService.create(`Finding all alerts (${this.alerts.size} total)`);
    return [...this.alerts.values()];
  }

  remove(ciudad: string): boolean {
    this.logger.log(`Removing alert for city: ${ciudad}`);
    this.logService.create(`Removing alert for city: ${ciudad}`);
    const removed = this.alerts.delete(ciudad);
    if (removed) {
      this.logger.log(`Alert removed for city: ${ciudad}`);
      this.logService.create(`Alert removed for city: ${ciudad}`);
    } else {
      this.logger.warn(`Alert not found for city: ${ciudad}`);
      this.logService.create(`Alert not found for city: ${ciudad}`);
    }
    return removed;
  }
}
