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
//createApp({model: postgreModel})

async function runKafka() {
  await ensureTopic("test-topic")
  
  await produceMessage("test-topic", "ESTE ES MI MENSAJE QUE SE ENVIA POR KAFKA");
  await consumeMessage("test-topic");
  
}

kafkaEmitter.on("Mensaje-Kafka", ({topic, partition, value}) => {
  console.log('⚡ Evento recibido en app.mjs:');
  console.log(`   🧩 Topic: ${topic}`);
  console.log(`   🔢 Partición: ${partition}`);
  console.log(`   💬 Mensaje: ${value}`);
}) 

runKafka().catch(console.error)
