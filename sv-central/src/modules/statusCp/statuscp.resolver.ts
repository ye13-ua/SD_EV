import { Resolver, Args, Mutation, Query} from '@nestjs/graphql';
import { StatusCpService } from './statuscp.service';
import { StatusCpInput } from './dto/status-cp.input';
import { StatusCP } from './entities/statuscp.entity';


@Resolver(() => StatusCP)
export class StatusCpResolver {
	constructor(private statusCpService: StatusCpService) {}
	
	//---------------------------- UPDATE ----------------------------
	@Mutation(() => Boolean, { name: "updateStatusCP", description: "Para enviar el estado del cp"})
	updateStatusCp(@Args("statusCpInput") statusCpInput: StatusCpInput): Promise<boolean> {
		return this.statusCpService.updateStatus(statusCpInput);
	}

	@Query(() => [StatusCP], {name: "readAllStatusCP", description: "Para devolver todos los estados de los cps guardados en memoria"})
	readAllStatusCP(): StatusCP[] {
		return this.statusCpService.readAllStatusCP();
	}

}
