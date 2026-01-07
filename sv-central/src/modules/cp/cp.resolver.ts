import { Query, Resolver, Args, Mutation} from '@nestjs/graphql';
import { CpService } from './cp.service';
import { CP } from './entities/cp.entity';
import { RegisterCpInput } from './dto/register-cp.input';
import { UpdateCpInput } from './dto/update-cp.input';

@Resolver(() => CP)
export class CpResolver {
	constructor(private cpService: CpService) {}


	//---------------------------- AUTETICATE ----------------------------
	@Mutation(() => CP, {name: "authenticateCp", description: "Autetica el CP en la base de datos"})
	authenticateCp(@Args("registerCpInput") registerCpInput: RegisterCpInput): Promise<CP> {
		return this.cpService.authenticateCp(registerCpInput)
	}

	//---------------------------- READ ----------------------------
	@Query(() => [CP], {name: "findAllCps", description: "Devuelve todos los cps de la base de datos"})
	findAll(): Promise<CP[]> {
		return this.cpService.findAll()
	}

	@Query(() => [String], {name: "findAllCitiesCp", description: "Devuelve todas las ciudades de los cps"})
	findAllCitiesCp(): Promise<string[]> {
		return this.cpService.findAllCitiesCp()
	}

	@Query(() => CP , {name: "findOneCp", description: "Devuelve el cp que coincida con el id de entrada"})
	findOne(@Args("id") id: string): Promise<CP> {
		return this.cpService.findOne(id);
	}
	//---------------------------- UNLINK ----------------------------
	@Mutation(() => Boolean, { name: "unlinkCp", description: "Desvincula un CP por id" })
	unlinkCp(@Args("id") id: string): Promise<boolean> {
		return this.cpService.unlink(id);
	}
		//---------------------------- UPDATE ----------------------------
	@Mutation(() => CP, {name: "updateCp", description: "Actualiza un cp"})
	updateCp(@Args("updateCpInput") updateCpInput: UpdateCpInput): Promise<CP> {
		return this.cpService.update(updateCpInput);
	}
}
