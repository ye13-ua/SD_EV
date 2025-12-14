import { ObjectType, Field, Int } from '@nestjs/graphql';
import { CreateDateColumn, Entity, PrimaryColumn } from 'typeorm';

@Entity()
@ObjectType()
export class Log {

  @PrimaryColumn({type: "bigint"})
  @Field(() => Number, { description: 'TimeStamp of the action' })
  timestamp: number;

  @PrimaryColumn({type: 'varchar', length: 360})
  @Field(() => String)
  description: string
}
