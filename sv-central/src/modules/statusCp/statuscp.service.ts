import { Injectable, UnauthorizedException, Logger } from '@nestjs/common';
import { StatusCpInput} from './dto/status-cp.input';
import { StatusCP } from './entities/statuscp.entity';
import { Interval } from '@nestjs/schedule';
import { CpService } from '../cp/cp.service';
import { createDecipheriv } from 'crypto';
import { AlertService } from '../alert/alert.service';
import { CommandService } from '../command/command.service';
import { LogService } from '../logsmod/log.service';


type CPType = "ACTIVE" | "WAITING" | "OUT_OF_SERVICE" | "CHARGING_CENTRAL" | "BROKEN" | "DISCONNECTED" | "FINISHED_CHARGING" | "CHANGED_LOCATION"

@Injectable()
export class StatusCpService {
	private readonly logger = new Logger(StatusCpService.name);
	private activeCPs = new Map<string, StatusCP>();
	private stoppedCPsByAlert = new Set<string>(); // CPs detenidos por alerta

	constructor(private readonly cpService: CpService, 
		private readonly alertService: AlertService,
		private readonly commandService: CommandService,
		private readonly logService: LogService
	){
		this.logger.log('StatusCpService initialized');
	}

	decryptJson<StatusCP>( payload: { iv: string; ciphertext: string; tag: string }, keyHex: string,): StatusCP 
	{
		this.logger.debug(`Decrypting payload with IV: ${payload.iv.substring(0, 8)}...`);
		this.logService.create(`Decrypting payload with IV: ${payload.iv.substring(0, 8)}...`);

		try {
			const key = Buffer.from(keyHex, 'hex');

			const decipher = createDecipheriv(
				'aes-256-gcm',
				key,
				Buffer.from(payload.iv, 'hex'),
			);

			decipher.setAuthTag(Buffer.from(payload.tag, 'hex'));

			const decrypted = Buffer.concat([
				decipher.update(Buffer.from(payload.ciphertext, 'hex')),
				decipher.final(),
			]);

			const decryptedString = decrypted.toString('utf8');
			const result = JSON.parse(decryptedString) as StatusCP;
			this.logger.debug('Successfully decrypted and parsed payload');
			this.logService.create('Successfully decrypted and parsed payload');
			return result;
		} catch (error) {
			this.logger.error(`Decryption failed: ${error.message}`, error.stack);
			this.logService.create(`Decryption failed: ${error.message}`);
			throw new UnauthorizedException('Invalid encryption credentials or corrupted payload');
		}
	}



	//---------------------------- CREATE ----------------------------
	
	async updateStatus(statusCpInput: StatusCpInput): Promise<boolean> {
		this.logger.log(`Updating status for CP: ${statusCpInput.id}`);
		this.logService.create(`Updating status for CP: ${statusCpInput.id}`);

		const bdCp = await this.cpService.findOne(statusCpInput.id);
		
		if (!bdCp || !bdCp.symmetricKey) {
			this.logger.error(`CP ${statusCpInput.id} not found or missing symmetric key`);
			throw new Error(`CP ${statusCpInput.id} not found or missing symmetric key`);
		}
		
		// Si decryptJson falla, la excepción se propaga automáticamente al cliente
		const statuscp = this.decryptJson<StatusCP>(statusCpInput, bdCp.symmetricKey);
		
		this.logger.debug(`CP ${statuscp.id} status: ${statuscp.estado}`);
		this.logService.create(`CP ${statuscp.id} status: ${statuscp.estado}`);

		switch (statuscp.estado as CPType) {
			case "ACTIVE":
				this.logger.debug(`CP ${statuscp.id} is ACTIVE`);
				break;
			case "WAITING":
				this.logger.debug(`CP ${statuscp.id} is WAITING`);
				break;
			case "CHARGING_CENTRAL":
				this.logger.debug(`CP ${statuscp.id} is CHARGING_CENTRAL`);
				break;
			case "FINISHED_CHARGING":
				this.logger.debug(`CP ${statuscp.id} FINISHED_CHARGING`);
				this.commandService.postCommand({
					command: "TICKET",
					price: statuscp.price,
					driverId: statuscp.driverId,
					cpId: statuscp.id,
					target: "ONE"
				});
				break;
			case "OUT_OF_SERVICE":
				this.logger.warn(`CP ${statuscp.id} is OUT_OF_SERVICE`);
				break;
			case "BROKEN":
				this.logger.error(`CP ${statuscp.id} is BROKEN`);
				this.logService.create(`CP ${statuscp.id} reported BROKEN status`);
				break;
			case "DISCONNECTED":
				this.logger.warn(`CP ${statuscp.id} is DISCONNECTED`);
				break;
		}


		this.activeCPs.set(statuscp.id, {...statuscp, timeStamp: Date.now()});
		this.logger.log(`Successfully updated status for CP: ${statuscp.id}`);
		return true
	}

	readAllStatusCP(): StatusCP[] {
		this.logger.debug('Reading all status CPs');
		this.logService.create('Reading all status CPs');

		this.updateAllStatusCP();
		const result = [...this.activeCPs.values()];
		this.logger.debug(`Returning ${result.length} CPs`);
		this.logService.create(`Returning ${result.length} CPs`);
		
		return result;
	}

	readAllActiveStatusCP(): StatusCP[] {
		this.logger.debug('Reading all active status CPs');
		this.logService.create('Reading all active status CPs');
		this.updateAllStatusCP();
		const result = [...this.activeCPs.values()].filter((cp) => {
			return cp.estado === "ACTIVE"
		});
		this.logger.debug(`Returning ${result.length} active CPs`);
		this.logService.create(`Returning ${result.length} active CPs`);
		return result;
	}

	//---------------------------- DELETE ----------------------------
	/**
	 * Elimina todos los cps de los activos a todos los que no hayan hayan actualizado su estado en los ulitmos 10 segundos
	 */
	@Interval(10_000)
	updateAllStatusCP(): void {
    const before = this.activeCPs.size;
    this.logger.debug(`Checking ${before} CPs for inactivity`);
	this.logService.create(`Checking ${before} CPs for inactivity`);
    
    [...this.activeCPs.values()].forEach((cp) => {
			const timeSinceUpdate = Date.now() - cp.timeStamp;
			if(timeSinceUpdate > 10_000) {
				this.logger.warn(`Removing inactive CP: ${cp.id} (inactive for ${timeSinceUpdate}ms)`);
				this.logService.create(`Removing inactive CP: ${cp.id} (inactive for ${timeSinceUpdate}ms)`);
				this.activeCPs.delete(cp.id);
			}
    	});
    	const removed = before - this.activeCPs.size;
    	if(removed > 0) {
			this.logger.log(`Cleaned ${removed} inactive CPs`);
			this.logService.create(`Cleaned ${removed} inactive CPs`);
		}
	}

	//---------------------------- HELPERS ----------------------------
	@Interval(10_000)
    checkAlertCps(): void {
        this.logger.debug('Checking for CPs in alert cities');
		this.logService.create('Checking for CPs in alert cities');

        const alertCities = this.alertService.findAll().map(alert => alert.ciudad);
        
        if (alertCities.length === 0) {
            this.logger.debug('No alert cities found');
			this.logService.create('No alert cities found');
            // Si no hay alertas pero hay CPs detenidos, reiniciarlos
            if (this.stoppedCPsByAlert.size > 0) {
                this.logger.log(`No more alerts. Restarting ${this.stoppedCPsByAlert.size} stopped CPs`);
                this.logService.create(`No more alerts. Restarting ${this.stoppedCPsByAlert.size} stopped CPs`);
                this.stoppedCPsByAlert.forEach(cpId => {
                    const cp = this.activeCPs.get(cpId);
                    if (cp) {
                        this.logger.log(`Sending START command to CP ${cpId} (alert cleared)`);
						this.logService.create(`Sending START command to CP ${cpId} (alert cleared)`);
                        this.commandService.postCommand({
                            command: "START",
                            cpId: cpId,
                            target: "ONE"
                        });
                    }
                });
                this.stoppedCPsByAlert.clear();
            }
            return;
        }
        
        this.logger.debug(`Found ${alertCities.length} alert cities: ${alertCities.join(', ')}`);
		this.logService.create(`Found ${alertCities.length} alert cities: ${alertCities.join(', ')}`);
        
        // CPs en ciudades con alerta que están activos
        const cpsinAlert = alertCities.flatMap((city) => {
            return [...this.activeCPs.values()]
                .filter(cp => cp.city === city)
                .filter(cp => cp.estado === "ACTIVE");
        });
        
        // Reiniciar CPs que ya no están en ciudades de alerta
        const cpsToRestart = [...this.stoppedCPsByAlert].filter(cpId => {
            const cp = this.activeCPs.get(cpId);
            return cp && !alertCities.includes(cp.city);
        });
        
        cpsToRestart.forEach(cpId => {
            this.logger.log(`Sending START command to CP ${cpId} (city no longer in alert)`);
			this.logService.create(`Sending START command to CP ${cpId} (city no longer in alert)`);
            this.commandService.postCommand({
                command: "START",
                cpId: cpId,
                target: "ONE"
            });
            this.stoppedCPsByAlert.delete(cpId);
        });

        // Detener CPs en ciudades con alerta (reenviar en cada check)
        if (cpsinAlert.length > 0) {
            this.logger.warn(`Found ${cpsinAlert.length} active CPs in alert cities`);
			this.logService.create(`Found ${cpsinAlert.length} active CPs in alert cities`);
            cpsinAlert.forEach(cp => {
                const isFirstTime = !this.stoppedCPsByAlert.has(cp.id);
                
                if (isFirstTime) {
                    this.logger.warn(`Sending STOP command to CP ${cp.id} in city ${cp.city} (Temperature < 0°C) [FIRST TIME]`);
					this.logService.create(`Sending STOP command to CP ${cp.id} in city ${cp.city} (Temperature < 0°C) [FIRST TIME]`);
                } else {
                    this.logger.debug(`Re-sending STOP command to CP ${cp.id} (ensuring delivery)`);
					this.logService.create(`Re-sending STOP command to CP ${cp.id} (ensuring delivery)`);
                }
                
                // Enviar comando STOP en cada iteración para asegurar que llegue
                this.commandService.postCommand({
                    command: "STOP",
                    cpId: cp.id,
                    target: "ONE"
                });
                
                this.stoppedCPsByAlert.add(cp.id);
            });
        } else {
            this.logger.debug('No active CPs found in alert cities');
			this.logService.create('No active CPs found in alert cities');
        }
    }
}

