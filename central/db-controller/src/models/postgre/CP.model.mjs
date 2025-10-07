import { DataTypes } from "sequelize";
import { sequelize } from "../../db/connection.mjs";
import { validateParcialCP } from "../../schemas/CP.schema.mjs";

//ORM 
export const CP = sequelize.define("CP",{
    ID_UUID: {
        type: DataTypes.UUID,
        primaryKey: true,
        allowNull: false,
    },
    Ubicacion: {
        type: DataTypes.STRING(100),
        allowNull: false,
    },
    Precio_KWH: {
        type: DataTypes.DOUBLE,
        allowNull: false
    }
},{
    tableName: "CPs",
    timestamps: false
}
)

export class CPModel {
    static async ReadAll() {
        try{
            const CPs = await CP.findAll();

            const CpsJSON = CPs.map(c => c.toJSON());
            return CpsJSON
        } catch(err){
            console.log("Error al leer todo",err); //TODO eliminar
            return
        }
    }
    static async Create({body}) {
        try {
            const CP = validateParcialCP(body);
            const CreatedCP = await CP.Create({
                ID_UUID: CP.data.ID_UUID,
                Ubicacion: CP.data.ubicacion,
                Precio_KWH: CP.data.precio_KWH
            })
            console.log("CP creado: ",CreatedCP.toJSON()); //TODO eliminar
            return CreatedCP.toJSON();
        } catch (err) {
            console.log("Error al insertar",err); //TODO eliminar
            return
        }
    }
}