
//servidor http
import express, { response } from "express";
import { createCPRouter } from "./routes/CP.routes.mjs";
import { postgreModel } from "./models/postgre/postgre.mjs";
import { sequelize } from "./db/connection.mjs";
//Para hacer post
import axios from "axios"
//tracker
import { tracker } from "./utils/activityTracker.mjs";

//kafka
import { consumeMessage, produceMessage, ensureTopic, kafkaEmitter, kafkaEvent } from "./controllers/kafka.controller.mjs"

//.env
import dotenv from "dotenv"
dotenv.config()

//sockets
import {Server} from "socket.io"
import { createServer } from "node:http";

let ActiveCPs = [];

export const createApp = async ({model}) => {
  
//--------------------------------- DB CONTROLLER ---------------------------------
  //crea un servidor http con express
  const app = express();
  
  //Borra la base de datos al iniciar la app: DEBUG
  await sequelize.sync(  
    //{force: true} 
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

  //Socket de creacion de CPS
  const CP_Central_Create_Socket = process.env.CP_CENTRAL_CREATE_SOCKET;
  //Socket de estado de CP
  const CP_Central_Status_Socket = process.env.CP_CENTRAL_STATUS_SOCKET;
  //Socket para enviar comandos desde el view a los CPS
  const View_Central_CMD_Socket = process.env.VIEW_CENTRAL_CMD_SOCKET;

  const CPsEndPoint = "http://localhost:4000/CPs";

  io.on("connection", (socket) => {
    
    console.log("Cliente conectado:", socket.id);

//--------------------------------- SOCKET CP_Central_Create_Socket ----------------------------------- DEBUG = FALSE
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

//--------------------------------- SOCKET CP_Central_Status_Socket ----------------------------------- DEBUG = FALSE
    socket.on(CP_Central_Status_Socket, async (data) => {
      if(data.isChanged){
        console.log(`CP ${data.ID_UUID} cambio de estado a -> ${data.Estado}`);
      }
    
      let exists = false;
      
     //ACTUALIZA EL ESTADO DE LOS ACTIVECPS en RAM
      ActiveCPs.forEach(e => {
        if(e.ID_UUID === data.ID_UUID){
          e.Estado = data.Estado
          e.Timestamp = data.Timestamp
          exists = true
          //ACTUALIZA LOS IDS ACTIVOS
          tracker.update(data.ID_UUID);
        }
      })

      //AGREGA A ACTIVE CP
      if(!exists) {
        readed = await axios.get(`${CPsEndPoint}:${data.ID_UUID}`);
        const cp = readed.data;
        ActiveCPs.push({...cp, Estado: data.Estado});
        
        //ACTUALIZA LOS IDS ACTIVOS
        tracker.update(data.ID_UUID);
      }
    })

//--------------------------------- SOCKET View_Central_CMD_Socket ------------------------------------ DEBUG = FALSE
    socket.on(View_Central_CMD_Socket, async (data) => {
      /*
        data = {
          action:
          target: UUID / "ALL"
          driver_id: UUID
          price: float
        }

      */
      await produceMessage(CENTRAL_CP_COMMANDS, data);
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

const {CENTRAL_DRIVER_COMMANDS, CENTRAL_CP_COMMANDS, DRIVER_COMMANDS} = process.env;

async function runKafka() {

  await ensureTopic(CENTRAL_DRIVER_COMMANDS)
  await ensureTopic(CENTRAL_CP_COMMANDS)
  await ensureTopic(DRIVER_COMMANDS)
  
  await consumeMessage(DRIVER_COMMANDS);
  
  //await produceMessage(KAFKA_TOPIC_CENTRAL_CP_CMD, "ESTE ES MI MENSAJE QUE SE ENVIA POR KAFKA");
}

kafkaEmitter.on(kafkaEvent, async ({topic, partition, data}) => {
  switch (topic) {
    case DRIVER_COMMANDS:
      switch (data.action){
//--------------------------------- CASE REGISTER ----------------------------------- DEBUG = FALSE
        case "REGISTER":
        //TODO IMPLEMENTAR ?????
        break;
//--------------------------------- CASE READALL ------------------------------------ DEBUG = FALSE
        case "READALL":

          //AQUI MIRA Y ACTUALIZA TODOS LOS CPS ACTICOS
          const ActiveCPs = ActiveCPs.filter(e => tracker.isActive(e.ID_UUID));

          data = {
            action: "READALL_RESPONSE",
            driver_id: data.driver_id,
            cps: ActiveCPs
          }
          //ENVIAR DE VUELTA TODOS LOS CPS
          produceMessage(CENTRAL_DRIVER_COMMANDS, data);

        break;
//--------------------------------- CASE CONNECTCP ---------------------------------- DEBUG = FALSE
        case "CONNECTCP":
          // TODO VERIFICAR QUE LA VALIDACION NO SE HACE DESDE CENTRAL DE FORMA MANULA SINO QUE AQUI
          // TODO LOGS
          // TODO MOSTRAR CONEXION DE DRIVER CON CP EN FRONT

          // PEDIR CONFIRMACIÓN A CP PARA LA CONEXION VIENDO EL ESTADO POR SOCKETS
          // DENEGAR O ACEPTAR POR CENTRAL.DRIVER.COMMANDS

          const driverId = data.driver_id;

          const driverResponse = {
            action: "CONNECT_CP_RESPONSE",
            driver_id: data.driver_id,
            isValidated: false,
            cp_id: null,
          }

          const centralLogs = {
            action: "CONNECTION_LOGS",
            driver_id: data.driver_id,
            logs: ""
          }

          if(data.cp_id){ // TIENE CP_ID
            
            driverResponse.cp_id = data.cp_id;

            //------LOGS------
            centralLogs.logs = `[DRIVER ${driverId}] intentado conectarse al [CP ${driverResponse.cp_id}]`;
            console.log(centralLogs.logs);
            produceMessage(CENTRAL_DRIVER_COMMANDS, centralLogs);

            if(tracker.isActive(driverResponse.cp_id)){ //ESE CP_ID ES ACTIVO
              driverResponse.isValidated = true;
              
              //------LOGS------
              centralLogs.logs = `[DRIVER ${driverId}] LA CONEXION CON [CP ${driverResponse.cp_id}] fue VALIDA`;
              console.log(centralLogs.logs);
              produceMessage(CENTRAL_DRIVER_COMMANDS, centralLogs);
            
            } else { //ESE CP_ID NO ES ACTIVO
              
              //------LOGS------
              centralLogs.logs = `[DRIVER ${driverId}] LA CONEXION CON [CP ${driverResponse.cp_id}] NO fue VALIDA`;
              console.log(centralLogs.logs);
              produceMessage(CENTRAL_DRIVER_COMMANDS, centralLogs);
            }
            
          } else { //NO TIENE CP_ID
            
            //------LOGS------
            centralLogs.logs = `[DRIVER ${driverId}] intentado conectarse a un CP RANDOM`;
            console.log(centralLogs.logs);
            produceMessage(CENTRAL_DRIVER_COMMANDS, centralLogs);

            const active = ActiveCPs.find(e => e.Estado === "ACTIVE");
            if(active){
              driverResponse.cp_id = active.ID_UUID;
              driverResponse.isValidated = true;
              
              //------LOGS------
              centralLogs.logs = `[DRIVER ${driverId}] LA CONEXION CON [CP ${driverResponse.cp_id}] fue VALIDA`;
              console.log(centralLogs.logs);
              produceMessage(CENTRAL_DRIVER_COMMANDS, centralLogs);

            } else {
              
              //------LOGS------
              centralLogs.logs =  `[DRIVER ${driverId}] NO SE ENCONTRO CPS ACTIVOS`;
              console.log(centralLogs.logs);
              produceMessage(CENTRAL_DRIVER_COMMANDS, centralLogs);

            }
          }
        
          if(driverResponse.isValidated){ // SI SE VALIDA LA CONEXION
            const CPPayload = {
              target: driverResponse.cp_id,
              action: "CHARGE",
              driver_id: driverResponse.driver_id,
              target_charge: data.charge
            }
            produceMessage(CENTRAL_CP_COMMANDS, CPPayload) // ENVIA LOS DATOS A CP PARA EL FUNCIONAMIENTO ADECUADO
          }

          produceMessage(CENTRAL_DRIVER_COMMANDS, driverResponse);
        break;
//--------------------------------- CASE DISCONNECT --------------------------------- DEBUG = FALSE
        case "DISCONNECT":
          // CENTRAL.CP.COMMANDS -> action = DRIVER_DISCONNECT
          // CENTRAL.DRIVER.COMMANDS -> action = ticket
          /*
            data = {
              driver_id: ID
              cp_id: uuid
            }
              
          */    
          const driverPayload = {
            action: "TICKET",
            driver_id: data.driver_id,
            cp_id: data.driver_id,
            price: 999 //TODO CALCULAR
          }
          const CPPayload = {
              target: data.cp_id,
              action: "DRIVER_DISCONNECT",
              driver_id: data.driver_id
          }
          produceMessage(CENTRAL_CP_COMMANDS, CPPayload)
          produceMessage(CENTRAL_DRIVER_COMMANDS, driverPayload);
        break;
      }
        
    break;
    default:
      console.log("Mensaje enviado por un topico incorrecto:",topic);
    break;
  }
}) 

runKafka().catch(console.error)

await createApp({model: postgreModel})

agregarCPs();

