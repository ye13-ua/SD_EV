import { Query, Resolver, Args} from '@nestjs/graphql';
import { CpService } from './cp.service';
import { CP } from './entities/cp.type';

@Resolver(() => CP)
export class CpResolver {
    constructor(
        private cpService: CpService
    ) {}

    @Query(() => [CP], {name: "cps", description: "Devuelve todos los cps de la base de datos"})
    getAllCps() {
        return this.cpService //TODO
    }

    @Query(() => CP , {name: "cp", description: "Devuelve el cp que coincida con el id de entrada"})
    getCp(@Args("id") id: string) {
        //TODO
    }

}
