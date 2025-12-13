import { Query, Resolver, Args, Mutation} from '@nestjs/graphql';
import { CpService } from './cp.service';
import { CP } from './entities/cp.entity';
import { CreateCpInput } from './dto/create-cp.input';
import { UpdateCpInput } from './dto/update-cp.input';
@Resolver(() => CP)
export class CpResolver {
	constructor(private cpService: CpService) {}
	//---------------------------- CREATE ----------------------------
	@Mutation(() => CP, {name: "createCp", description: "Crea un nuevo cp en la base de datos"})
	createCp(@Args("createCpInput") createCpInput: CreateCpInput): Promise<CP> {
		return this.cpService.create(createCpInput)
	}
	//Ambos tienen la misma funcionalidad xdxd
	@Mutation(() => CP, {name: "registerCp", description: "Registra el CP en la base de datos"})
	registerCP(@Args("registerCpInput") registerCpInput: CreateCpInput): Promise<CP> {
		return this.cpService.create(registerCpInput)
	}

	//---------------------------- READ ----------------------------
	@Query(() => [CP], {name: "findAllCps", description: "Devuelve todos los cps de la base de datos"})
	findAll(): Promise<CP[]> {
		return this.cpService.findAll()
	}

	@Query(() => CP , {name: "findOneCp", description: "Devuelve el cp que coincida con el id de entrada"})
	findOne(@Args("id") id: string): Promise<CP> {
		return this.cpService.findOne(id);
	}
	//---------------------------- UPDATE ----------------------------
	@Mutation(() => CP, {name: "updateCp", description: "Actualiza un cp"})
	updateCp(@Args("updateCpInput") updateCpInput: UpdateCpInput): Promise<CP> {
		return this.cpService.update(updateCpInput);
	}

	//---------------------------- DELETE ----------------------------
	@Mutation(() => Boolean, { name: "deleteCp", description: "Elimina un CP por id" })
	removeCp(@Args("id") id: string): Promise<boolean> {
		return this.cpService.remove(id);
	}

	

}
