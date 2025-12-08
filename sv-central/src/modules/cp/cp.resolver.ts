import { Query, Resolver, Args} from '@nestjs/graphql';
import { CpService } from './cp.service';
import { CP } from './entities/cp.entity';

@Resolver(() => CP)
export class CpResolver {
    constructor(private cpService: CpService) {}

    @Query(() => [CP], {name: "cps", description: "Devuelve todos los cps de la base de datos"})
    getAllCps(): Promise<CP[]> {
        return this.cpService.getAllCps() //TODO
    }

    @Query(() => CP , {name: "cp", description: "Devuelve el cp que coincida con el id de entrada"})
    getCp(@Args("id") id: string): Promise<CP> {
        return this.cpService.getCp(id);
    }

}
