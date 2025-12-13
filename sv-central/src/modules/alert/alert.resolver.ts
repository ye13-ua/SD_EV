import { Resolver, Query, Mutation, Args, Int } from '@nestjs/graphql';
import { AlertService } from './alert.service';
import { Alert } from './entities/alert.entity';
import { CreateAlertInput } from './dto/create-alert.input';

@Resolver(() => Alert)
export class AlertResolver {
  constructor(private readonly alertService: AlertService) {}

  @Mutation(() => Alert)
  createAlert(@Args('createAlertInput') createAlertInput: CreateAlertInput): Alert {
    return this.alertService.create(createAlertInput);
  }

  @Query(() => [Alert], { name: 'findAllCiudades' })
  findAllCiudades(): Alert[] {
    return this.alertService.findAll();
  }

  @Mutation(() => Alert)
  removeAlert(@Args('ciudad', { type: () => String }) ciudad: string): boolean {
    return this.alertService.remove(ciudad);
  }
}
