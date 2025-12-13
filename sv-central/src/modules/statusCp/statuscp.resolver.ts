import { Resolver, Args, Mutation} from '@nestjs/graphql';
import { StatusCpService } from './statuscp.service';
import { StatusCpInput } from './dto/status-cp.input';
import { StatusCP } from './entities/statuscp.entity';
import { Query } from '@nestjs/common';

@Resolver(() => StatusCP)
export class StatusCpResolver {
	constructor(private statusCpService: StatusCpService) {}
	
	//---------------------------- UPDATE ----------------------------
	@Mutation(() => Boolean, { name: "updateStatusCP", description: "Para enviar el estadoa del cp aqui"})
	updateStatusCp(@Args("statusCpInput") statusCpInput: StatusCpInput): Promise<Boolean> {
		return this.statusCpService.updateStatus(statusCpInput);
	}

	@Query(() => [StatusCP], {})
	readAllStatusCP(): Promise<any> {
		return this.statusCpService.readAllStatusCP();
	}

}
