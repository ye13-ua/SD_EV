import { Kafka } from "kafkajs";
import dotenv from "dotenv"
import EventEmitter from "node:events"

dotenv.config()

const kafkaInstance = new Kafka({
    clientId: "EV_Central",
    brokers: [process.env.KAFKA_BOOTSTRAP],
})

export const kafkaEmitter = new EventEmitter();


//TODO Verificar groupID

const consumer = kafkaInstance.consumer({ groupId: "central_cmd"})

export async function consumeMessage(topic) {

    await consumer.connect();
    // TODO cambiar el topico, sacar de env
    await consumer.subscribe({ topic: topic, fromBeginning: true})


    await consumer.run({
        eachMessage: async ({ topic, partition, message }) => {
            const msg = message.value.toString();
            
            console.log(`Recibido: ${msg}`);
            
            kafkaEmitter.emit("Mensaje-Kafka", {
                topic,
                partition,
                value: msg
            })
            
        },
    });

}

