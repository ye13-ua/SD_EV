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
import { consumeMessage, produceMessage, ensureTopic, kafkaEmitter } from "./controllers/kafka.controller.mjs"
import dotenv from "dotenv"

dotenv.config()

export const  createApp = async ({model}) => {
  const app = express();
  await sequelize.sync({force: true}); //TODO Quitar force 
  const PORT = process.env.PORT ?? 4000;

  app.use(express.json());
  app.disable("x-powered-by");
  //TODO Eliminar
  app.get("/", (req, res) => {
    res.send("Hola mundo");
  });

  app.use((req, res, next) => {
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

const {KAFKA_TOPIC_CP_CENTRAL_CREATE, KAFKA_TOPIC_CENTRAL_CP_CMD} = process.env;

async function runKafka() {


  await ensureTopic(KAFKA_TOPIC_CP_CENTRAL_CREATE)
  await ensureTopic(KAFKA_TOPIC_CENTRAL_CP_CMD)
  
  await consumeMessage(KAFKA_TOPIC_CP_CENTRAL_CREATE);
  
  
  
  //await produceMessage("test-topic", "ESTE ES MI MENSAJE QUE SE ENVIA POR KAFKA");
  
}

kafkaEmitter.on("Mensaje-Kafka", ({topic, partition, value}) => {
  switch (topic) {
    //TODO Crear ITEM
    case KAFKA_TOPIC_CP_CENTRAL_CREATE:
      

    break;

  }
  
  
  
  console.log(` Mensaje: ${value}`);
  console.log(` Topico: ${topic}`)
  console.log(` Partición: ${partition}`)
}) 

runKafka().catch(console.error)

createApp({model: postgreModel})