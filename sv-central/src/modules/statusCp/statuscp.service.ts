import { Injectable } from '@nestjs/common';
import { StatusCpInput} from './dto/status-cp.input';
import { StatusCP } from './entities/statuscp.entity';
import { Interval } from '@nestjs/schedule';
import { CpService } from '../cp/cp.service';
import { createDecipheriv } from 'crypto';
import { AlertService } from '../alert/alert.service';
import { CommandService } from '../command/command.service';


type CPType = "ACTIVE" | "WAITING" | "OUT_OF_SERVICE" | "CHARGING_CENTRAL" | "BROKEN" | "DISCONNECTED" | "FINISHED_CHARGING" | "CHANGED_LOCATION"

@Injectable()
export class StatusCpService {
	


	constructor(private readonly cpService: CpService, 
		private readonly alertService: AlertService,
		private readonly commandService: CommandService
	){}

	
	private activeCPs = new Map<string, StatusCP>();

	decryptJson<StatusCP>( payload: { iv: string; ciphertext: string; tag: string }, keyHex: string,): StatusCP 
	{
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

		return JSON.parse(decrypted.toString('utf8')) as StatusCP;
	}



	//---------------------------- CREATE ----------------------------
	
	async updateStatus(statusCpInput: StatusCpInput): Promise<boolean> {
		
		const bdCp = await this.cpService.findOne(statusCpInput.id)
		
		const statuscp = this.decryptJson<StatusCP>(statusCpInput, bdCp.symmetricKey)
		//...statusCpInput, timeStamp: Date.now()
		
		switch (statuscp.estado as CPType) {
			case "ACTIVE":
				break;
			case "WAITING":
				break;
			case "CHARGING_CENTRAL":
				break;
			case "FINISHED_CHARGING":
				break;
			case "OUT_OF_SERVICE":
				break;
			case "BROKEN":
				break;
			case "DISCONNECTED":
				break;
			case "CHANGED_LOCATION":
				break;
			default:
				return false;
		}


		this.activeCPs.set(statuscp.id, {...statuscp, timeStamp: Date.now()});
		return true
	}

	readAllStatusCP(): StatusCP[] {
		this.updateAllStatusCP();
		return [...this.activeCPs.values()]
	}

	readAllActiveStatusCP(): StatusCP[] {
		this.updateAllStatusCP();
		return [...this.activeCPs.values()].filter((cp) => {
			return cp.estado === "ACTIVE"
		})
	}

	//---------------------------- DELETE ----------------------------
	/**
	 * Elimina todos los cps de los activos a todos los que no hayan hayan actualizado su estado en los ulitmos 10 segundos
	 */
	@Interval(10_000)
	updateAllStatusCP(): void {
    const before = this.activeCPs.size;
    [...this.activeCPs.values()].forEach((cp) => {
			if((Date.now() - cp.timeStamp) > 10_000) {
				console.log(`[StatusCP] Removing inactive CP: ${cp.id}`);
				this.activeCPs.delete(cp.id);
			}
    	});
    	const removed = before - this.activeCPs.size;
    	if(removed > 0) console.log(`[StatusCP] Cleaned ${removed} inactive CPs`);
	}

	//---------------------------- HELPERS ----------------------------
	@Interval(10_000)
    checkAlertCps(): void {
        const cities = this.alertService.findAll().map(alert => alert.ciudad);
        
        // Flatten: convierte array de arrays en array plano
        const cpsinAlert = cities.flatMap((city) => {
            return [...this.activeCPs.values()]
                .filter(cp => cp.city === city)
                .filter(cp => cp.estado === "ACTIVE");
        });


        if (cpsinAlert.length > 0) {
            console.log(`[AlertCP] Found ${cpsinAlert.length} active CPs in alert cities`);
            cpsinAlert.forEach(cp => {
                console.log(`  - CP ${cp.id} in city ${cp.city} (ALERT: Temperature < 0°C)`);
				this.commandService.postCommand({
					command: "STOP",
					cpId: cp.id,
					target: "ONE"
				});
			});
        }
    }
}

