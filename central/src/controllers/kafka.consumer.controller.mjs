import { Kafka } from "kafkajs";
import dotenv from "dotenv"

dotenv.config()

const kafka = new Kafka({
    clientId: "EV_Central",
    brokers: [process.env.KAFKA_BOOTSTRAP]
})

export async function consumeMessage() {
    const consumer = kafka.consumer({ groupId: "central_cmd"})
    await consumer.connect();
    // TODO cambiar el topico, sacar de env
    await consumer.subscribe({ topic: "test-topic", fromBeginning: true})


    await consumer.run({
        eachMessage: async ({ topic, partition, message }) => {
            console.log(`Recibido: ${message.value.toString()}`);
        },
    });

}
