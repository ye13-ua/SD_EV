import { Resolver, Query, Mutation, Args, Int } from '@nestjs/graphql';
import { LogService } from './log.service';
import { Log } from './entities/log.entity';
import { CreateLogInput } from './dto/create-log.input';

@Resolver(() => Log)
export class LogResolver {
  constructor(private readonly logService: LogService) {}

  @Mutation(() => Log)
  createLog(@Args('createLogInput') createLogInput: CreateLogInput): Promise<Log> {
    return this.logService.create(createLogInput);
  }

  @Query(() => [Log], { name: 'log' })
  findAll(): Promise<Log[]> {
    return this.logService.findAll();
  }

}
