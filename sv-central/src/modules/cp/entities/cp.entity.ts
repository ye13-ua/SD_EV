import { ObjectType, Field, Float} from "@nestjs/graphql"
import { Column, Entity, PrimaryColumn } from "typeorm"

@Entity()
@ObjectType()
export class CP {

    @PrimaryColumn({type: "uuid"})
    @Field(() => String)
    id: string

    @Column({type: "varchar", length: 120})
    @Field(() => String)
    ciudad: string

    @Column({type: "varchar", length: 360})
    @Field(() => String)
    calle: string

    @Column({type: "float"})
    @Field(() => Float)
    precio_kwh: number
// ----------------------- REGISTRO -----------------------
    @Column({type: "varchar", length: 420 ,nullable: true})
    @Field(() => String, {nullable: true})
    clientSecretHash: string

    @Column({type: "varchar", length: 420, nullable: true})
    @Field(() => String, {nullable: true})
    clientSecret: string
// ----------------------- AUTENTICACIÓN -----------------------
    @Column({type: "varchar", length: 420, nullable: true})
    @Field(() => String, {nullable: true})
    symmetricKey: string
}
