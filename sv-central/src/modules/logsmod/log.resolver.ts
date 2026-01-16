import { Resolver, Query, Mutation, Args, Int } from '@nestjs/graphql';
import { LogService } from './log.service';
import { Log } from './entities/log.entity';

@Resolver(() => Log)
export class LogResolver {
  constructor(private readonly logService: LogService) {}

  @Mutation(() => Log)
  createLog(@Args('description') description: string): Promise<Log> {
    return this.logService.create(description);
  }

  @Query(() => [Log], { name: 'log' })
  findAll(): Promise<Log[]> {
    return this.logService.findAll();
  }

}
