import { Kafka } from "kafkajs";
import dotenv from "dotenv"

dotenv.config()

const kafka = new Kafka({
    clientId: "EV_Central",
    brokers: [process.env.KAFKA_BOOTSTRAP]
})

export async function produceMessage(message) {
    const producer = kafka.producer();
    await producer.connect();
    // TODO cambiar el topico, sacar de env
    await producer.send({
        topic: "test-topic",
        messages: [{ value: message}]
    })

    console.log("Enviando mensaje", message);
    await producer.disconnect()
}