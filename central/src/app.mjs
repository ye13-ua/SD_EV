
//servidor http
import express from "express";
import { createCPRouter } from "./routes/CP.routes.mjs";
import { postgreModel } from "./models/postgre/postgre.mjs";
import { sequelize } from "./db/connection.mjs";

//kafka
import { consumeMessage, produceMessage, ensureTopic, kafkaEmitter } from "./controllers/kafka.controller.mjs"

//.env
import dotenv from "dotenv"

//sockets
import {Server} from "socket.io"
import { createServer } from "node:http";
import os from "os"

dotenv.config()

export const createApp = async ({model}) => {
  
  //--------------------------------- DB CONTROLLER ---------------------------------
  //crea un servidor http con express
  const app = express();
  
  //Borra la base de datos al iniciar la app: DEBUG
  await sequelize.sync({force: true}); //TODO Quitar force 

  //Puerto que se saca de 
  const PORT = process.env.PORT ?? 4000;

  //Para el view de los datos
  app.set("view engine", "ejs");
  app.set("views", "./src/views")  
  app.use(express.static("public"));

  //Para que la app use json
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  //Para que el envio de los datos en json no muestre info sobre la app
  app.disable("x-powered-by");
  
  //--------------------------------- SOCKETS ---------------------------------

  const server = createServer(app);

  const io = new Server(server, {connectionStateRecovery: {}})

  //Implmentar


  /*
    DATOS DESDE MOTOR (Python) 
    {
      ID_UUID: "XXX"
      Estado: 1,2,3,4,5
      
      -> Si 3:
      Vehiculo: {
        Id:
        Carga:
        PrecioCarga:
      }
      -> fin si
    }
  
  
  */


  io.on("connection", (socket) => {
    console.log("Cliente conectado:", socket.id);
    
    const data = {
      test: "XDXD"
    }

    

    io.emit("NuevaConexion", data)

    socket.on("disconnect", () => {
      console.log("Cliente desconectado", socket.id)
    })
  })
  
  //--------------------------------- REST ---------------------------------


  app.get("/", (req, res) => {
    //Aqui se conecta para controlar la central
    res.redirect("localhost:4000/CPs")
  });

  app.use((req, res, next) => {
    res.on('finish', () => {
        
      console.log(`Se ejecutó la operación ${req.method} -> ${req.originalUrl}`);
    });

    next();
  })

  app.use("/CPs",createCPRouter({CPModel: model.CPModel}))

  server.listen(PORT, () => {
    console.log(`Servidor escuchando en el puerto ${PORT}`);
  });



}

 //--------------------------------- KAFKA ---------------------------------

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