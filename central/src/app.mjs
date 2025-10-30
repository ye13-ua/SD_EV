
//servidor http
import express from "express";
import { createCPRouter } from "./routes/CP.routes.mjs";
import { postgreModel } from "./models/postgre/postgre.mjs";
import { sequelize } from "./db/connection.mjs";
//Para hacer post
import axios from "axios"

//kafka
import { consumeMessage, produceMessage, ensureTopic, kafkaEmitter, kafkaEvent } from "./controllers/kafka.controller.mjs"

//.env
import dotenv from "dotenv"
dotenv.config()

//sockets
import {Server} from "socket.io"
import { createServer } from "node:http";



export const createApp = async ({model}) => {
  
  //--------------------------------- DB CONTROLLER ---------------------------------
  //crea un servidor http con express
  const app = express();
  
  //Borra la base de datos al iniciar la app: DEBUG
  await sequelize.sync(  
    {force: true} 
  ); //TODO Quitar force 

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

  /*
    DATOS DESDE MOTOR (Python) 
    {
      ID_UUID: "XXX"
      Estado: "CHARGING"
      
      -> fin si
    }
  */
  //Socket de creacion de CPS
  const CP_Central_Create_Socket = process.env.CP_CENTRAL_CREATE_SOCKET;
  //Socket de estado de CP
  const CP_Central_Status_Socket = process.env.CP_CENTRAL_STATUS_SOCKET;
  //Socket para enviar comandos desde el view a los CPS
  const View_Central_CMD_Socket = process.env.VIEW_CENTRAL_CMD_SOCKET;
  const CPsEndPoint = "http://localhost:4000/CPs";

  io.on("connection", (socket) => {
    
    console.log("Cliente conectado:", socket.id);
    
    //TODO Probar
    // Socket que se encarga en crear los CPS
    socket.on(CP_Central_Create_Socket, async (data) => {
      try{
        const response = await axios.post(CPsEndPoint, data);
        if(!response.data.error) {
          console.log("CP Creado ->",response.data.ID_UUID);

          //AQUI SE DEBERIA DE ENVIAR UN STATUS CREATED

        } else {
          console.log("Fallo al crear CP ->",response.data.error);
        } 
      } catch (err) {
        console.log("Error al enviar los datos a la db ->",err.message);
      }
    })

    //CP de estado para poner los cambios en la consola, isChanged sirve para que no imprima el cambio de estado cada vez que lleguen datos por este socket
    socket.on(CP_Central_Status_Socket, (data) => {
      if(data.isChanged){
        console.log(`CP ${data.ID_UUID} cambio de estado a -> ${data.ID_UUID}`);
      }
    })

    socket.on("disconnect", () => {
      console.log("Cliente desconectado", socket.id)
    })
  })
  
  //--------------------------------- REST ---------------------------------


  app.get("/", (req, res) => {
    //Aqui se conecta para controlar la central
    res.redirect(CPsEndPoint);
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

const {KAFKA_TOPIC_CENTRAL_CP_CMD} = process.env;

async function runKafka() {

  await ensureTopic(KAFKA_TOPIC_CENTRAL_CP_CMD)
  
  await consumeMessage(KAFKA_TOPIC_CP_CENTRAL_CREATE);
  


  //await produceMessage(KAFKA_TOPIC_CENTRAL_CP_CMD, "ESTE ES MI MENSAJE QUE SE ENVIA POR KAFKA");
}

kafkaEmitter.on(kafkaEvent, ({topic, partition, value}) => {
  switch (topic) {
    
  }
  console.log(` Mensaje: ${value}`);
  console.log(` Topico: ${topic}`)
  console.log(` Partición: ${partition}`)
}) 

runKafka().catch(console.error)

createApp({model: postgreModel})