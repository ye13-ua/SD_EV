import { ObjectType, Field, Float} from "@nestjs/graphql"
import { Column, Entity, PrimaryColumn } from "typeorm"

@Entity()
@ObjectType()
export class CP {

    @PrimaryColumn({type: "uuid"})
    @Field()
    id: string

    @Column()
    @Field()
    ciudad: string

    @Column({type: "float"})
    @Field(() => Float)
    precio_kwh: number
// ----------------------- REGISTRO -----------------------
    @Column({nullable: true})
    @Field({nullable: true})
    clientSecretHash: string

    @Column({nullable: true})
    @Field({nullable: true})
    clientSecret: string
// ----------------------- AUTENTICACIÓN -----------------------
    @Column({nullable: true})
    @Field({nullable: true})
    symmetricKey: string
}
