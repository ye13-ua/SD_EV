/**
 * MODULO X
 * CONTROLADOR V
 * ENRUTADOR X
 * ESQUEMA V
 * CONFIG
 */


import express from "express";
import { createCPRouter } from "./routes/CP.routes.mjs";
import { postgreModel } from "./models/postgre/postgre.mjs";
import { sequelize } from "./db/connection.mjs";


export const  createApp = async ({model}) => {
  const app = express();
  await sequelize.sync();
  const PORT = process.env.PORT ?? 4000;

  app.use(express.json());
  app.disable("x-powered-by");
  //TODO Eliminar
  app.get("/", (req, res) => {
    res.send("Hola mundo");
  });

  app.use((req, res, next) => {
    console.log("Esto es lo que llego -> ",req.body);
    res.on('finish', () => {
        
      console.log(`Se ejecutó la operación ${req.method} -> ${req.originalUrl}`);
    });

    next();
  })
  //TODO Implementar metodo que pase de cola a http
  app.use("/CPs",createCPRouter({CPModel: model.CPModel}))

  app.listen(PORT, () => {
    console.log(`Servidor escuchando en el puerto ${PORT}`);
  });
}

createApp({model: postgreModel})
