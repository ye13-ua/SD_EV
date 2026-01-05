import { ObjectType, Field, Float} from "@nestjs/graphql"
import { Column, Entity, PrimaryColumn } from "typeorm"

@Entity()
@ObjectType()
export class CP {

    @PrimaryColumn({type: "uuid"})
    @Field(() => String)
    id: string

    @Column()
    @Field(() => String)
    ciudad: string

    @Column({type: "float"})
    @Field(() => Float)
    precio_kwh: number
// ----------------------- REGISTRO -----------------------
    @Column({nullable: true})
    @Field(() => String, {nullable: true})
    clientSecretHash: string

    @Column({nullable: true})
    @Field(() => String, {nullable: true})
    clientSecret: string
// ----------------------- AUTENTICACIÓN -----------------------
    @Column({nullable: true})
    @Field(() => String, {nullable: true})
    symmetricKey: string
}
