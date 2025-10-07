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

export const createApp = ({model}) => {
  const app = express();
  const PORT = process.env.PORT ?? 4000;

  app.use(express.json());
  app.disable("x-powered-by");

  app.get("/", (req, res) => {
    res.send("Hola mundo");
  });

  app.use((req, res, next) => {
   
    res.on('finish', () => {
        
      console.log(`Se ejecutó la operación ${req.method} -> ${req.originalUrl}`);
    });

    next();
  })

  app.use("/Cps",createCPRouter({model: model.CPModel}))

  app.listen(PORT, () => {
    console.log(`Servidor escuchando en el puerto ${PORT}`);
  });
}

createApp({model: postgreModel})
