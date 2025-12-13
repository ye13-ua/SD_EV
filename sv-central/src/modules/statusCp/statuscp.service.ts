import { Injectable } from '@nestjs/common';
import { StatusCpInput} from './dto/status-cp.input';
import { StatusCP } from './entities/statuscp.entity';


@Injectable()
export class StatusCpService {

	private memCps = new Map<string, StatusCP>

	//---------------------------- CREATE ----------------------------

	async updateStatus(statusCpInput: StatusCpInput): Promise<boolean> {
		
		this.memCps.set(statusCpInput.id, {...statusCpInput});
		return true
	}

	async readAllStatusCP(): Promise<StatusCP[]> {
		return Array.from(this.memCps.values())
	}

	//---------------------------- DELETE ----------------------------

}
