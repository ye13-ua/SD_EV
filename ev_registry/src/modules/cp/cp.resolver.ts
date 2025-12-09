import { Query, Resolver, Args, Mutation} from '@nestjs/graphql';
import { CpService } from './cp.service';
import { CP } from './entities/cp.entity';
import { CreateCpDto } from './dto/create-cp.dto';

@Resolver(() => CP)
export class CpResolver {
    constructor(private cpService: CpService) {}
    //---------------------------- CREATE ----------------------------
    @Mutation(() => CP, {name: "createCp", description: "Crea un nuevo cp en la base de datos"})
    createCp(@Args("cpDto") cpDto: CreateCpDto): Promise<CP> {
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

    //---------------------------- DELETE ----------------------------
}
