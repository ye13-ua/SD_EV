import { Kafka } from "kafkajs";
import dotenv from "dotenv"

dotenv.config()

const kafkaInstance = new Kafka({
    clientId: "EV_Central",
    brokers: [process.env.KAFKA_BOOTSTRAP],
})

const producer = kafkaInstance.producer();

export async function produceMessage(topic, message) {
    await producer.connect();

    await producer.send({
        topic: topic,
        messages: [{ value: message}]
    })

    console.log("Enviando mensaje", message);
    await producer.disconnect()
}
