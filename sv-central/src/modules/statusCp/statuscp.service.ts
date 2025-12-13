import { Injectable } from '@nestjs/common';
import { StatusCpInput} from './dto/status-cp.input';
import { StatusCP } from './entities/statuscp.entity';
import { Interval } from '@nestjs/schedule';

@Injectable()
export class StatusCpService {

	private activeCPs = new Map<string, StatusCP>

	//---------------------------- CREATE ----------------------------

	updateStatus(statusCpInput: StatusCpInput): boolean {
		this.activeCPs.set(statusCpInput.id, {...statusCpInput});
		return true
	}

	readAllStatusCP(): StatusCP[] {
		return [...this.activeCPs.values()]
	}

	//---------------------------- DELETE ----------------------------
	@Interval(10_000)
	updateAllStatusCP(): void {
		[...this.activeCPs.values()].forEach((cp) => {
			if((Date.now() - cp.timeStamp) > 15_000) this.activeCPs.delete(cp.id)
		})
	}

}
