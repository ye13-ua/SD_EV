import { Query, Resolver, Args, Mutation} from '@nestjs/graphql';
import { CpService } from './cp.service';
import { CP } from './entities/cp.entity';
import { CreateCpDto } from './dto/create-cp.input';
import { UpdateCpDto } from './dto/update-cp.input';

@Resolver(() => CP)
export class CpResolver {
    constructor(private cpService: CpService) {}
    //---------------------------- CREATE ----------------------------
    @Mutation(() => CP, {name: "createCp", description: "Crea un nuevo cp en la base de datos"})
    createCp(@Args("cp") cpDto: CreateCpDto): Promise<CP> {
        return this.cpService.createCP(cpDto)
    }
    //---------------------------- READ ----------------------------
    @Query(() => [CP], {name: "readAllCps", description: "Devuelve todos los cps de la base de datos"})
    readAllCps(): Promise<CP[]> {
        return this.cpService.readAllCps()
    }

    @Query(() => CP , {name: "readCp", description: "Devuelve el cp que coincida con el id de entrada"})
    readCp(@Args("id") id: string): Promise<CP> {
        return this.cpService.readCp(id);
    }
    //---------------------------- UPDATE ----------------------------
    @Mutation(() => CP, {name: "updateCp", description: "Actualiza un cp"})
    updateCp(@Args("cp") updateCpDto: UpdateCpDto): Promise<CP> {
        return this.cpService.updateCp(updateCpDto);
    }

    //---------------------------- DELETE ----------------------------
    @Mutation(() => Boolean, { name: "deleteCp", description: "Elimina un CP por id" })
    deleteCp(@Args("id") id: string): Promise<boolean> {
        return this.cpService.deleteCp(id);
    }

}
