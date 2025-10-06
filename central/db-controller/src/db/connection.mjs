import { Sequelize } from "sequelize";

//CONEXION A LA BASE DE DATOS
export const sequelize = new Sequelize ("evcharging","usuario","contraseña", {
    host: "db",
    dialect: "postgres",
    logging: false
})