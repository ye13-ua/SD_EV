import { ObjectType, Field, Float} from "@nestjs/graphql"

@ObjectType()
export class StatusCP {

    @Field()
    id: string
    
    // ACTIVE - WAITING - OUT_OF_SERVICE - CHARGING_CENTRAL - BROKEN - DISCONNECTED |!| FINISHED_CHARGING
    @Field({nullable: true})     
    estado: string

    @Field({nullable: true})
    isChanged: boolean

    @Field({nullable: true})
    timeStamp: number;

    @Field({nullable: true})
    kafkaOK: boolean
    
    @Field(() => Float, {nullable: true, })
    alreadyCharged: number

    @Field({nullable: true})
    driverId: string

    //IF -> FINISHED_CHARGING
    @Field({nullable: true})
    price: number
}
