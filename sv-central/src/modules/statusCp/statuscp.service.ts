import { Injectable } from '@nestjs/common';
import { StatusCpInput} from './dto/status-cp.input';
import { StatusCP } from './entities/statuscp.entity';
import { Interval } from '@nestjs/schedule';

@Injectable()
export class StatusCpService {

	private activeCPs = new Map<string, StatusCP>

	//---------------------------- CREATE ----------------------------

	updateStatus(statusCpInput: StatusCpInput): boolean {
		this.activeCPs.set(statusCpInput.id, {...statusCpInput, timeStamp: Date.now()});
		return true
	}

	readAllStatusCP(): StatusCP[] {
		this.updateAllStatusCP();
		return [...this.activeCPs.values()]
	}

	readAllActiveStatusCP(): StatusCP[] {
		this.updateAllStatusCP();
		return [...this.activeCPs.values()].filter((cp) => {
			cp.estado === "ACTIVE"
		})
	}

	//---------------------------- DELETE ----------------------------
	/**
	 * Elimina todos los cps de los activos a todos los que no hayan hayan actualizado su estado en los ulitmos 10 segundos
	 */
	@Interval(10_000)
	updateAllStatusCP(): void {
		[...this.activeCPs.values()].forEach((cp) => {
			if((Date.now() - cp.timeStamp) > 10_000) this.activeCPs.delete(cp.id)
		})
	}

}
