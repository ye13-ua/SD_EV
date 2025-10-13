import { DataTypes } from "sequelize";
import { sequelize } from "../../db/connection.mjs";
import { validateParcialCP } from "../../schemas/CP.schema.mjs";

//ORM 
export const CP = sequelize.define("CP",{
    ID_UUID: {
        type: DataTypes.UUID,
        primaryKey: true,
    },
    Ubicacion: {
        type: DataTypes.STRING(100),
        allowNull: false
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
            if(CPs.length > 0) {
                const CpsJSON = CPs.map(c => c.toJSON());
                return CpsJSON
            } else {
                return {error: "Base de datos vacia"};
            }
            
        } catch(err){
            console.log("Error al leer todo",err); //TODO eliminar
            return
        }
    }
    static async Create({body}) {
        try {
            const validCP = validateParcialCP(body);
            if (await CP.findByPk(validCP.data.ID_UUID)) {
                return {error: "Valor ya existente"}
            } else {
                const CreatedCP = await CP.bulkCreate([validCP.data])
                return CreatedCP[0].dataValues;
            }
        } catch (err) {
            console.log("Error al insertar",err); //TODO eliminar
            return
        }
    }
}