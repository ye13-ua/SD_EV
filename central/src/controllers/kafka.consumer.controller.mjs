import { Kafka, logLevel } from "kafkajs";
import EventEmitter from "node:events"



const kafkaInstance = new Kafka({
    clientId: "EV_Central",
    brokers: [process.env.KAFKA_BOOTSTRAP],
    logLevel: logLevel.ERROR
})

export const kafkaEmitter = new EventEmitter();
export const kafkaEvent = "Mensaje-Kafka";

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
            
            kafkaEmitter.emit(kafkaEvent, {
                topic,
                partition,
                value: msg
            })
            
        },
    });

}

