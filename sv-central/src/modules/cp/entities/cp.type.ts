import {ObjectType, Field, Float} from "@nestjs/graphql"

@ObjectType()
export class CP {
    @Field()
    id: string

    @Field()
    ciudad: string

    @Field()
    calle: string

    @Field(() => Float)
    precio_kwh: number
}
